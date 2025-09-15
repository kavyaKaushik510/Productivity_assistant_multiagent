# agents/calendar_optimiser.py
from typing import List
from agents.schemas import TimeBlock, CalendarResult, CalendarEvent
from tools.calendar_provider import get_events, propose_time_blocks


class CalendarOptimiser:
    """Fetch events and propose time blocks for tasks."""

    def run(self, tasks: List[dict], block_hours: int = 1) -> CalendarResult:
        logs: List[str] = []
        events: List[CalendarEvent] = []

        try:
            events = get_events(5)
            logs.append(f"Fetched {len(events)} upcoming events.")
        except Exception as e:
            return CalendarResult(events=[], proposals=[], logs=[f"ERROR: Calendar fetch failed - {e}"])

        try:
            raw = propose_time_blocks(tasks, block_hours=block_hours)
            proposals = [TimeBlock(**b) for b in raw]
            logs.append(f"Proposed {len(proposals)} time blocks.")
        except Exception as e:
            return CalendarResult(events=events, proposals=[], logs=logs + [f"ERROR: Proposal failed - {e}"])

        return CalendarResult(events=events, proposals=proposals, logs=logs)
