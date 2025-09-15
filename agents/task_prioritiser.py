from agents.schemas import Task
from datetime import datetime


class TaskPrioritiser:
    """Assigns priorities to tasks based on deadlines and keywords."""

    def run(self, tasks: list[Task]) -> dict:
        logs, updated = [], []
        today = datetime.today().date()

        for t in tasks:
            priority = "LOW"

            if t.due_date:
                try:
                    due = datetime.strptime(t.due_date, "%Y-%m-%d").date()
                    if due <= today:
                        priority = "HIGH"
                    elif (due - today).days <= 2:
                        priority = "HIGH"
                    else:
                        priority = "MED"
                except Exception:
                    pass
            elif any(v in t.title.lower() for v in ["review", "check", "look at"]):
                priority = "MED"

            updated_task = t.copy(update={"priority": priority})
            updated.append(updated_task)
            logs.append(f"Task '{t.title}' → priority {priority}")

        return {"tasks": updated, "logs": logs}
