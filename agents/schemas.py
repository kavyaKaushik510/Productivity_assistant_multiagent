from pydantic import BaseModel, Field
from typing import List, Optional



class Task(BaseModel):
    id: str
    title: str
    source: str
    priority: Optional[str] = None   # HIGH, MED, LOW
    due_raw: Optional[str] = None
    due_date: Optional[str] = None
    estimate_min: Optional[int] = None
    status: str = "PENDING"
    confidence: float


class Summary(BaseModel):
    subject: str
    category: str
    text: str


class EmailResponse(BaseModel):
    summary: str
    category: str
    tasks: List[Task] = []


class MeetingTask(BaseModel):
    title: str
    priority: str = Field(..., description="HIGH, MED, LOW")
    due_raw: Optional[str] = None
    due_date: Optional[str] = None


class MeetingResponse(BaseModel):
    summary: str = Field(..., description="Main summary of the meeting")
    discussion_points: List[str] = Field(default_factory=list, description="Key points discussed")
    tasks: List[MeetingTask] = Field(default_factory=list, description="Action items for Kavya")