# tests/test_calendar_agent.py
from agents.calendar_optimiser import CalendarOptimiser

if __name__ == "__main__":
    # Dummy tasks to schedule
    tasks = [
        {"id": "t1", "title": "Finish design draft", "priority": "HIGH"},
        {"id": "t2", "title": "Write project report", "priority": "MED"},
        {"id": "t3", "title": "Prepare meeting notes", "priority": "LOW"},
    ]

    agent = CalendarOptimiser()
    result = agent.run(tasks, block_hours=1)

    print("===Upcoming Events ===")
    if not result.get("events"):
        print("(none)")
    else:
        for e in result["events"]:
            # each event is a dict, so use schema helper
            from agents.schemas import CalendarEvent
            event = CalendarEvent(**e)
            print(f"- {event.convert_readable()}")

    print("\n===Proposed Time Blocks ===")
    if not result.get("proposals"):
        print("(none)")
    else:
        from agents.schemas import TimeBlock
        for b in result["proposals"]:
            block = TimeBlock(**b)
            linked = f" (task={block.linked_task_id})" if block.linked_task_id else ""
            print(f"- {block.convert_readable()}{linked}")

    print("\n=== 📝 Logs ===")
    for log in result.get("logs", []):
        print("-", log)
