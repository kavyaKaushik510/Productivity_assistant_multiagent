from datetime import datetime


class TaskPrioritiser:
    """Assigns priorities to tasks based on deadlines and keywords."""

    def run(self, tasks: list[dict]) -> dict:
        logs, updated_tasks = [], []
        today = datetime.today().date()

        for t in tasks:
            t_data = dict(t)  # normalise to dict
            priority = "LOW"

            if t_data.get("due_date"):
                try:
                    due = datetime.strptime(t_data["due_date"], "%Y-%m-%d").date()
                    if due <= today:
                        priority = "HIGH"   # due today or overdue
                    elif (due - today).days <= 2:
                        priority = "HIGH"   # due within 2 days
                    else:
                        priority = "MED"
                except Exception:
                    pass
            elif any(v in t_data.get("title", "").lower() for v in ["review", "check", "look at"]):
                priority = "MED"

            # store priority in dict (not in Task schema)
            t_data["priority"] = priority
            updated_tasks.append(t_data)
            logs.append(f"Task '{t_data['title']}' → priority {priority}")

        return {"tasks": updated_tasks, "logs": logs}

