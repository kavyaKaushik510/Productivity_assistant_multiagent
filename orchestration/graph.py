# orchestration/graph.py
from langgraph.graph import StateGraph, END
from orchestration.state import WorkflowState
from agents.email_manager import EmailManager
from agents.task_prioritiser import TaskPrioritiser
from agents.calendar_optimiser import CalendarOptimiser


# Instantiate agents
email_agent = EmailManager()
prioritiser = TaskPrioritiser()
calendar = CalendarOptimiser()


# Node functions (merge-aware dicts)
def fetch_and_classify_emails(state: WorkflowState) -> WorkflowState:
    result = email_agent.run(n=5)
    return {
        "summaries": result.get("summaries", []),
        "tasks": result.get("tasks", []),
        "logs": state.get("logs", []) + result.get("logs", []),
    }


def prioritise_tasks(state: WorkflowState) -> WorkflowState:
    result = prioritiser.run(state.get("tasks", []))
    return {
        "summaries": state.get("summaries", []),
        "tasks": result.get("tasks", []),
        "logs": state.get("logs", []) + result.get("logs", []),
    }

def optimise_calendar(state: WorkflowState) -> WorkflowState:
    result = calendar.run(state.get("tasks", []))  # now returns dict
    return {
        "summaries": state.get("summaries", []),
        "tasks": state.get("tasks", []),
        "logs": state.get("logs", []) + result.get("logs", []),
        "calendar": result,
    }

#Build LangGraph 
workflow = StateGraph(WorkflowState)

workflow.add_node("emails", fetch_and_classify_emails)
workflow.add_node("prioritise", prioritise_tasks)
workflow.add_node("calendar", optimise_calendar)

workflow.set_entry_point("emails")
workflow.add_edge("emails", "prioritise")
workflow.add_edge("prioritise", "calendar")
workflow.add_edge("calendar", END)

# Compile to runnable app
app = workflow.compile()
