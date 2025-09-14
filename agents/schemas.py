from pydantic import BaseModel, Field
from typing import List, Optional


class Task(BaseModel):
    title: str
    confidence: float
    due_raw: Optional[str] = None  # e.g., "by Friday"
    due_date: Optional[str] = None  # e.g., "2025-09-19"


class EmailResponse(BaseModel):
    summary: str
    category: str
    tasks: List[Task]


class MeetingTask(BaseModel):
    title: str
    priority: str = Field(..., description="HIGH, MED, LOW")
    due_raw: Optional[str] = None
    due_date: Optional[str] = None


class MeetingResponse(BaseModel):
    summary: str = Field(..., description="Main summary of the meeting")
    discussion_points: List[str] = Field(default_factory=list, description="Key points discussed")
    tasks: List[MeetingTask] = Field(default_factory=list, description="Action items for Kavya")