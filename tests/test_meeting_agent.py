from agents.meeting_summariser import MeetingSummariser
from collections import defaultdict


def test_meeting_summariser():
    agent = MeetingSummariser()
    result = agent.run("data/sample_transcript.txt")

    print("\n=== Meeting Summariser Test ===")
    for log in result["logs"]:
        print("LOG:", log)

    print("\n--- Summary ---")
    print(result["summary"])

    print("\n--- Discussion Points ---")
    for point in result["discussion"]:
        print(f"- {point}")

    print("\n--- Tasks for Kavya ---")
    grouped = defaultdict(list)
    for t in result["tasks"]:
        grouped[t["priority"]].append(t)

    for priority in ["HIGH", "MED", "LOW"]:
        tasks = grouped.get(priority, [])
        if tasks:
            print(f"\n{priority} Priority:")
            for t in tasks:
                print(
                    f"- {t['title']} "
                    f"(due={t['due_date'] or t['due_raw'] or 'no deadline'}, "
                    f"confidence={t['confidence']:.2f})"
                )


if __name__ == "__main__":
    test_meeting_summariser()
