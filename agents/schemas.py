from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Task(BaseModel):
    id: Optional[str] = None
    title: str
    source: Optional[str] = None
    priority: str = "MED"   #default
    due_raw: Optional[str] = None
    due_date: Optional[str] = None
    estimate_min: Optional[int] = None
    status: str = "PENDING"
    confidence: Optional[float] = 1.0

class Summary(BaseModel):
    subject: str
    category: str
    text: str


class EmailResponse(BaseModel):
    summary: str
    category: str
    tasks: List[Task] = []

#Meeting Agent Schemas
class MeetingResponse(BaseModel):
    summary: str = Field(..., description="Main summary of the meeting")
    discussion_points: List[str] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)

#Calendar Agent Schemas
class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str   # ISO8601 string
    end: str     # ISO8601 string

    def convert_readable(self) -> str:
        """Human-friendly formatting for printing."""
        start_dt = datetime.fromisoformat(self.start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(self.end.replace("Z", "+00:00"))
        start_str = start_dt.strftime("%a %d %b, %H:%M")
        end_str = end_dt.strftime("%H:%M")
        return f"{self.title}: {start_str} → {end_str}"
    
class TimeBlock(BaseModel):
    start: str
    end: str
    title: str
    linked_task_id: Optional[str] = None

    def convert_readable(self) -> str:
        """Human-friendly formatting for proposed blocks."""
        start_dt = datetime.fromisoformat(self.start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(self.end.replace("Z", "+00:00"))
        start_str = start_dt.strftime("%a %d %b, %H:%M")
        end_str = end_dt.strftime("%H:%M")
        return f"{self.title}: {start_str} → {end_str}"


class CalendarResult(BaseModel):
    events: List[CalendarEvent] = []
    proposals: List[TimeBlock] = []
    logs: List[str] = []