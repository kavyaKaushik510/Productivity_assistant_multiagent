# orchestration/state.py
from typing import TypedDict, List, Optional
from agents.schemas import Summary, Task, CalendarResult

class WorkflowState(TypedDict, total=False):
    """Shared state structure across the workflow."""
    summaries: List[Summary]
    tasks: List[Task]
    logs: List[str]
    calendar: Optional[CalendarResult]
