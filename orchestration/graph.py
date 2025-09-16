# orchestration/graph.py
from langgraph.graph import StateGraph, END

from agents.email_manager import EmailManager
from agents.meeting_summariser import MeetingSummariser
from agents.task_prioritiser import TaskPrioritiser
from agents.calendar_optimiser import CalendarOptimiser
from agents.schemas import Task, MeetingTask


def build_graph(doc_id: str | None = None):
    # Instead of PlannerState, just use dict
    graph = StateGraph(dict)

    email_agent = EmailManager()
    meeting_agent = MeetingSummariser()
    prioritiser = TaskPrioritiser()
    calendar_agent = CalendarOptimiser()

    # --- Node: Email Manager ---
    def run_email(state: dict):
        result = email_agent.run(n=5)
        state.setdefault("tasks", []).extend(result["tasks"])
        state.setdefault("summaries", []).extend(result["summaries"])
        state.setdefault("logs", []).extend(result["logs"])
        return state

    # --- Node: Meeting Summariser ---
    def run_meeting(state: dict):
        if doc_id:
            result = meeting_agent.run(doc_id)
            meeting_tasks = []
            for idx, mt in enumerate(result.tasks):
                if isinstance(mt, MeetingTask):
                    meeting_tasks.append(Task(
                        id=f"meeting_{idx}",
                        title=mt.title,
                        source="meeting",
                        priority=mt.priority,
                        due_raw=mt.due_raw,
                        due_date=mt.due_date,
                        estimate_min=None,
                        status="PENDING",
                        confidence=1.0,
                    ))
                elif isinstance(mt, Task):
                    meeting_tasks.append(mt)

            state.setdefault("tasks", []).extend(meeting_tasks)
            state.setdefault("logs", []).append("Processed meeting notes → tasks added")
        return state

    # --- Node: Task Prioritiser ---
    def run_prioritiser(state: dict):
        result = prioritiser.run(state["tasks"])
        state["tasks"] = result["tasks"]
        state.setdefault("logs", []).extend(result["logs"])
        return state

    # --- Node: Calendar Optimiser ---
    def run_calendar(state: dict):
        result = calendar_agent.run([t.dict() for t in state["tasks"]])
        state["events"] = result.events
        state["proposals"] = result.proposals
        state.setdefault("logs", []).extend(result.logs)
        return state

    # --- Build Graph ---
    graph.add_node("emails", run_email)
    graph.add_node("meeting", run_meeting)
    graph.add_node("prioritise", run_prioritiser)
    graph.add_node("calendar", run_calendar)

    graph.set_entry_point("emails")
    graph.add_edge("emails", "meeting")
    graph.add_edge("meeting", "prioritise")
    graph.add_edge("prioritise", "calendar")
    graph.add_edge("calendar", END)

    workflow = graph.compile()
    return workflow
