import datetime
from orchestration.graph import app
from agents.schemas import CalendarEvent, TimeBlock 


def save_logs(logs):
    """Append logs to logs.txt with a timestamped heading."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== Run at {now} ===\n")
        for l in logs:
            f.write(f"{l}\n")


def print_summaries(summaries):
    print("\n=== 📧 Summaries ===")
    groups = {"PROJECT": [], "ALERT": [], "MEETING": [], "OTHER": [], "PROMO": []}

    for s in summaries:
        groups.get(s.category, groups["OTHER"]).append(s)

    for cat in ["ALERT", "PROJECT", "MEETING", "OTHER"]:
        if groups[cat]:
            print(f"\n--- {cat} ---")
            for s in groups[cat]:
                print(f"- {s.subject}\n  {s.text}\n")



def print_tasks_grouped(tasks):
    print("\n=== ✅ Tasks ===")
    groups = {"HIGH": [], "MED": [], "LOW": []}
    for t in tasks:
        groups.get(t.priority or "LOW", groups["LOW"]).append(t)

    for level in ["HIGH", "MED", "LOW"]:
        if groups[level]:
            print(f"\n--- {level} Priority ---")
            for t in groups[level]:
                tag = "[MEETING]" if t.source == "meeting" else "[EMAIL]"
                due = f" | Due: {t.due_date}" if t.due_date else ""
                print(f"- {t.title} {tag}{due}")


def print_calendar(calendar):
    if not calendar:
        return

    print("\n=== 📅 Calendar Events ===")
    for e in calendar.get("events", []):
        ev = CalendarEvent(**e)   # rebuild model for formatting
        print(f"- {ev.convert_readable()}")

    print("\n=== 📌 Proposed Time Blocks ===")
    for b in calendar.get("proposals", []):
        tb = TimeBlock(**b)       # rebuild model for formatting
        print(f"- {tb.convert_readable()}")


def print_results(result):
    print_summaries(result.get("summaries", []))
    print_tasks_grouped(result.get("tasks", []))
    print_calendar(result.get("calendar"))


if __name__ == "__main__":
    state = {"summaries": [], "tasks": [], "logs": []}
    result = app.invoke(state)

    # save logs to file
    save_logs(result.get("logs", []))

    # pretty-print results
    print_results(result)

    print("\n(Logs saved to logs.txt)")
