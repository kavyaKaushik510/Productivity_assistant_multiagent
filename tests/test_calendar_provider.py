from tools.calendar_provider import get_events, propose_time_blocks

if __name__ == "__main__":
    events = get_events(5)
    print("=== Upcoming Events ===")
    for e in events:
        print("-", e["summary"], e["start"].get("dateTime"))

    dummy_tasks = [
        {"id": "t1", "title": "Prepare report"},
        {"id": "t2", "title": "Review code"},
    ]
    proposals = propose_time_blocks(dummy_tasks)
    print("\n=== Proposed Blocks ===")
    for p in proposals:
        print("-", p["title"], p["start"], "→", p["end"])

