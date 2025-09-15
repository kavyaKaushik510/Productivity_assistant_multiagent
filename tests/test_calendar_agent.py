# tests/test_calendar_agent.py
from agents.calendar_optimiser import CalendarOptimiser

if __name__ == "__main__":
    # Dummy tasks to schedule
    tasks = [
        {"id": "t1", "title": "Finish design draft"},
        {"id": "t2", "title": "Write project report"},
        {"id": "t3", "title": "Prepare meeting notes"},
    ]

    agent = CalendarOptimiser()
    result = agent.run(tasks, block_hours=1)

    print("=== Upcoming Events ===")
    if not result.events:
        print("(none)")
    else:
        for e in result.events:
            print(f"- {e.convert_readable()}")

    print("\n=== Proposed Time Blocks ===")
    if not result.proposals:
        print("(none)")
    else:
        for b in result.proposals:
            print(f"- {b.convert_readable()} (task={b.linked_task_id})")

    print("\n=== Logs ===")
    for log in result.logs:
        print("-", log)

