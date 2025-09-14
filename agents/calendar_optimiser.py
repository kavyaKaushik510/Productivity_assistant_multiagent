from tools.calendar_provider import get_events, propose_time_blocks


class CalendarOptimiser:
    def __init__(self, source_label: str = "calendar"):
        self.source_label = source_label

    def run(self, tasks: list[dict], block_hours: int = 1):
        logs, proposals = [], []
        try:
            events = get_events(5)
            logs.append(f"Fetched {len(events)} upcoming events from Google Calendar.")
        except Exception as e:
            return {"proposals": [], "logs": [f"ERROR: Calendar fetch failed - {e}"]}

        try:
            proposals = propose_time_blocks(tasks, block_hours=block_hours)
            logs.append(f"Proposed {len(proposals)} new time blocks for tasks.")
        except Exception as e:
            logs.append(f"ERROR: Failed to propose time blocks - {e}")

        return {"proposals": proposals, "logs": logs}