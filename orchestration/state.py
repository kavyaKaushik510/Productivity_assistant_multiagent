# orchestration/state.py
from pydantic import BaseModel
from typing import List
from agents.schemas import Task, TimeBlock, CalendarEvent


class PlannerState(BaseModel):
    """Holds shared state across the workflow."""
    tasks: List[Task] = []
    events: List[CalendarEvent] = []
    proposals: List[TimeBlock] = []
    logs: List[str] = []
