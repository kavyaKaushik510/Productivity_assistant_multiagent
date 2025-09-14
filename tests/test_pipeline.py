from agents.email_manager import EmailManager
from agents.task_prioritiser import TaskPrioritiser
from agents.calendar_optimiser import CalendarOptimiser
from collections import defaultdict


if __name__ == "__main__":
    print("=== PIPELINE DEMO: EMAIL → TASKS → PRIORITISE → CALENDAR ===\n")

    # 1. Fetch emails and extract tasks
    email_agent = EmailManager()
    email_result = email_agent.run(n=5)

    print("=== Email Summaries ===")
    for s in email_result["summaries"]:
        print("-", s)

    # 2. Prioritise tasks
    prioritiser = TaskPrioritiser()
    prioritised = prioritiser.run(email_result["tasks"])

    grouped_tasks = defaultdict(list)
    for t in prioritised["tasks"]:
        grouped_tasks[t["priority"]].append(t)

    print("\n=== Tasks by Priority ===")
    for level in ["HIGH", "MED", "LOW"]:
        print(f"\n[{level}]")
        if not grouped_tasks[level]:
            print("(none)")
        else:
            for t in grouped_tasks[level]:
                print(f"- {t['title']} (due={t.get('due_date')}, conf={t.get('confidence',0):.2f})")

    # 3. Propose calendar time blocks
    cal_agent = CalendarOptimiser()
    cal_result = cal_agent.run(prioritised["tasks"], block_hours=1)

    print("\n=== Proposed Time Blocks ===")
    if not cal_result["proposals"]:
        print("(none)")
    else:
        for b in cal_result["proposals"]:
            print(f"- {b['title']} {b['start']} → {b['end']}")

    # 4. Logs
    print("\n=== Logs ===")
    for log in email_result["logs"] + prioritised["logs"] + cal_result["logs"]:
        print("-", log)
