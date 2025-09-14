from agents.calendar_optimiser import CalendarOptimiser

if __name__ == "__main__":
    # Dummy tasks (normally these come from EmailManager/MeetingSummariser)
    dummy_tasks = [
        {"id": "t1", "title": "Finish design draft"},
        {"id": "t2", "title": "Write project report"},
    ]

    agent = CalendarOptimiser()
    result = agent.run(dummy_tasks, block_hours=1)

    # === Proposed Time Blocks ===
    print("=== Proposed Time Blocks ===")
    if not result["proposals"]:
        print("(none)")
    else:
        for b in result["proposals"]:
            print(f"- {b['title']} {b['start']} → {b['end']} (linked_task_id={b['linked_task_id']})")

    # === Logs ===
    print("\n=== Logs ===")
    for log in result["logs"]:
        print("-", log)
