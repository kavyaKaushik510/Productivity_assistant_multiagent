# tools/calendar_provider.py
from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agents.schemas import CalendarEvent

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = "secrets/token.json"
CREDS_PATH = "secrets/credentials.json"


def get_calendar_service():
    """Authenticate and return a Google Calendar service client."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_events(limit: int = 10) -> List[CalendarEvent]:
    """Fetch upcoming events from the primary calendar."""
    service = get_calendar_service()
    now = datetime.now(timezone.utc).isoformat()
    resp = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=limit,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events: List[CalendarEvent] = []
    for e in resp.get("items", []):
        events.append(
            CalendarEvent(
                id=e.get("id", ""),
                title=e.get("summary", "Untitled"),
                start=e.get("start", {}).get("dateTime") or e.get("start", {}).get("date"),
                end=e.get("end", {}).get("dateTime") or e.get("end", {}).get("date"),
            )
        )
    return events


def _parse_event_time(event: dict):
    """Return aware datetime if timed; None for all-day events."""
    if "dateTime" in event:
        return datetime.fromisoformat(event["dateTime"])
    if "date" in event:
        return None
    return None


def _busy_windows(events: List[CalendarEvent]) -> List[Tuple[datetime, datetime]]:
    """Convert CalendarEvent list into busy (start, end) windows in UTC."""
    busy = []
    for ev in events:
        start = _parse_event_time({"dateTime": ev.start} if "T" in ev.start else {"date": ev.start})
        end = _parse_event_time({"dateTime": ev.end} if "T" in ev.end else {"date": ev.end})
        if start and end:
            busy.append((start.astimezone(timezone.utc), end.astimezone(timezone.utc)))
    return busy


def propose_time_blocks(
    tasks: list[dict],
    block_hours: int = 1,
    work_start: int = 9,
    work_end: int = 18,
    lookahead_days: int = 3,
) -> list[dict]:
    """
    Propose free time blocks for tasks across today and the next N days.
    Returns list of dicts: {start, end, title, linked_task_id}.
    """
    now = datetime.now(timezone.utc)
    current = max(now, now.replace(hour=work_start, minute=0, second=0, microsecond=0))
    events = get_events(limit=50)
    busy = _busy_windows(events)

    proposals = []
    day_limit = now.date() + timedelta(days=lookahead_days)

    for t in tasks:
        scheduled = False
        while not scheduled:
            # roll forward if past work hours
            end_of_day = current.replace(hour=work_end, minute=0, second=0, microsecond=0)
            if current >= end_of_day:
                current = (current + timedelta(days=1)).replace(
                    hour=work_start, minute=0, second=0, microsecond=0
                )

            # stop if beyond lookahead
            if current.date() > day_limit:
                break

            block_end = current + timedelta(hours=block_hours)

            # check overlap
            overlap = any(bs < block_end and be > current for (bs, be) in busy)
            if not overlap and block_end <= end_of_day:
                proposals.append(
                    {
                        "start": current.isoformat(),
                        "end": block_end.isoformat(),
                        "title": t.get("title", "Task"),
                        "linked_task_id": t.get("id"),
                    }
                )
                current = block_end + timedelta(minutes=15)  # add buffer
                scheduled = True
            else:
                current = current + timedelta(minutes=30)  # advance slot

    return proposals
