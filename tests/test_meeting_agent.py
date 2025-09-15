# tests/test_meeting_agent.py
from agents.meeting_summariser import MeetingSummariser

if __name__ == "__main__":
    DOC_ID = "1Db_gPHiLzFE1HO4dBXB2RpLrdxTV8iAJAXF4RbaJekw"  # replace with a real Google Doc ID
    agent = MeetingSummariser()
    result = agent.run(DOC_ID)

    print("=== Meeting Summary ===")
    print(result.summary)

    print("\n=== Discussion Points ===")
    for p in result.discussion_points:
        print("-", p)

    print("\n=== Action Items for Kavya ===")
    for t in result.tasks:
        print(f"- {t.title} (priority={t.priority}, due={t.due_raw})")
