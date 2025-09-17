# agents/calendar_optimiser.py
from typing import List
from agents.schemas import TimeBlock, CalendarResult, CalendarEvent, Task
from tools.calendar_provider import get_events, propose_time_blocks


class CalendarOptimiser:
    """Fetch events and propose time blocks for tasks."""

    def run(self, tasks: List[Task], block_hours: int = 1) -> dict:
        logs: List[str] = []
        events: List[CalendarEvent] = []

        try:
            events = get_events(5)
            logs.append(f"Fetched {len(events)} upcoming events.")
        except Exception as e:
            return {
                "events": [],
                "proposals": [],
                "logs": [f"ERROR: Calendar fetch failed - {e}"],
            }

        try:
            # Normalize tasks to dicts before passing downstream
            task_dicts = [t.model_dump() if hasattr(t, "dict") else t for t in tasks]
            raw = propose_time_blocks(task_dicts, block_hours=block_hours)
            proposals = [TimeBlock(**b) for b in raw]
            logs.append(f"Proposed {len(proposals)} time blocks.")
        except Exception as e:
            return {
                "events": [e.model_dump() for e in events],
                "proposals": [],
                "logs": logs + [f"ERROR: Proposal failed - {e}"],
            }

        # Normalize CalendarResult to dict before returning
        result = CalendarResult(events=events, proposals=proposals, logs=logs)
        return result.model_dump()
