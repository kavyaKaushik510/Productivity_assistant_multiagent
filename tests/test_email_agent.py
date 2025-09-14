from agents.email_manager import EmailManager
from agents.task_prioritiser import TaskPrioritiser
from collections import defaultdict


if __name__ == "__main__":
    agent = EmailManager()
    result = agent.run(n=4)  # fetch last 10 emails

    # === Summaries grouped by category ===
    print("=== Summaries ===")
    grouped_summaries = defaultdict(list)
    for s in result["summaries"]:
        if "(" in s and ")" in s:
            cat = s.split("(")[1].split(")")[0]
        else:
            cat = "UNCAT"
        grouped_summaries[cat].append(s)

    for cat in ["ALERT", "PROJECT", "MEETING", "OTHER", "PROMO", "UNCAT"]:
        if grouped_summaries[cat]:
            print(f"\n[{cat}]")
            for s in grouped_summaries[cat]:
                print("-", s)

    # === Tasks grouped by priority ===
    print("\n=== Tasks ===")
    prioritizer = TaskPrioritiser()
    prioritized = prioritizer.run(result["tasks"])

    grouped_tasks = defaultdict(list)
    for t in prioritized["tasks"]:
        grouped_tasks[t["priority"]].append(t)

    for level in ["HIGH", "MED", "LOW"]:
        print(f"\n[{level} Priority]")
        if not grouped_tasks[level]:
            print("(none)")
        else:
            for t in grouped_tasks[level]:
                print(
                    f"- {t['title']} "
                    f"(due={t.get('due_date')}, conf={t.get('confidence', 0.0):.2f})"
                )

    # === Logs ===
    print("\n=== Logs ===")
    for log in result["logs"] + prioritized["logs"]:
        print("-", log)
