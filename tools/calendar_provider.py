from __future__ import annotations
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os, datetime
from datetime import datetime, timedelta, timezone

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None
    token_path = "secrets/token.json"
    creds_path = "secrets/credentials.json"
    
    # Load saved credentials if they exist
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Refresh or re-login if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs("secrets", exist_ok=True)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)


def get_events(n: int = 5):
    service = get_calendar_service()
    now = datetime.now(timezone.utc).isoformat()
    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=n,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    return result.get("items", [])


def parse_event_time(event_time: dict):
    """Return datetime (aware) if event has time; None if all-day event."""
    if "dateTime" in event_time:
        return datetime.fromisoformat(event_time["dateTime"])
    elif "date" in event_time:
        return None
    return None


def propose_time_blocks(tasks: list[dict], block_hours: int = 1, start_hour: int = 9, end_hour: int = 18):
    """
    Propose time blocks for tasks across today and future days if needed.
    - Each task gets `block_hours` length.
    - If today has no space, roll over to next day at `start_hour`.
    - Skips all-day events.
    - Works with UTC-aware datetimes.
    """
    now = datetime.now(timezone.utc)

    # Start scheduling from "now" or from today's start_hour (whichever is later)
    current = now
    if current.hour < start_hour:
        current = current.replace(hour=start_hour, minute=0, second=0, microsecond=0)

    proposals = []

    events = get_events(20)  # fetch more events ahead
    busy = []
    for e in events:
        start = parse_event_time(e["start"])
        end = parse_event_time(e["end"])
        if start and end:
            busy.append((start.astimezone(timezone.utc), end.astimezone(timezone.utc)))

    for t in tasks:
        scheduled = False
        while not scheduled:
            block_end = current + timedelta(hours=block_hours)
            end_of_day = current.replace(hour=end_hour, minute=0, second=0, microsecond=0)

            # If we've run past today's end hour → move to next day
            if block_end > end_of_day:
                current = (current + timedelta(days=1)).replace(
                    hour=start_hour, minute=0, second=0, microsecond=0
                )
                continue

            # Check overlap
            overlap = any(bs <= current < be for (bs, be) in busy)
            if not overlap:
                proposals.append({
                    "start": current.isoformat(),
                    "end": block_end.isoformat(),
                    "title": t["title"],
                    "linked_task_id": t["id"]
                })
                current = block_end + timedelta(minutes=15)  # add buffer
                scheduled = True
            else:
                # move forward in 30-min increments until free
                current = current + timedelta(minutes=30)

    return proposals