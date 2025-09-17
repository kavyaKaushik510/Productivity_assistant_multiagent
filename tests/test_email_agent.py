# tests/test_email_agent.py
from agents.email_manager import EmailManager
from agents.task_prioritiser import TaskPrioritiser
from collections import defaultdict
from datetime import datetime
import os

if __name__ == "__main__":
    agent = EmailManager()
    result = agent.run(n=3)  # fetch last 10 emails

    print("=== EMAIL AGENT DEMO ===")
    print(f"(Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")

    # === Summaries grouped by category ===
    grouped_summaries = defaultdict(list)
    for s in result["summaries"]:
        grouped_summaries[s.category].append(s)

    print("=== Summaries ===")
    for cat in ["ALERT", "PROJECT", "MEETING", "OTHER"]:
        if grouped_summaries[cat]:
            print(f"\n[{cat}]")
            for s in grouped_summaries[cat]:
                print(f"- [{s.subject}] {s.text}")

    # === Tasks grouped by priority ===
    print("\n=== Tasks ===")
    prioritizer = TaskPrioritiser()
    prioritized = prioritizer.run(result["tasks"])

    grouped_tasks = defaultdict(list)
    for t in prioritized["tasks"]:
        grouped_tasks[t.priority].append(t)

    for level in ["HIGH", "MED", "LOW"]:
        print(f"\n[{level}]")
        if not grouped_tasks[level]:
            print("(none)")
        else:
            for t in grouped_tasks[level]:
                print(f"- {t.title} (due={t.due_date}, conf={t.confidence:.2f})")

    # === Logs ===
    print("\n=== Logs ===")
    for log in result["logs"] + prioritized["logs"]:
        print("-", log)



