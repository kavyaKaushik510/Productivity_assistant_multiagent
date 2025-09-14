from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tools.llm import get_llm
from agents.schemas import MeetingResponse
import dateparser
import os


def normalize_due(raw: str) -> str | None:
    if not raw:
        return None
    dt = dateparser.parse(raw, settings={"PREFER_DATES_FROM": "future"})
    if dt:
        return dt.strftime("%Y-%m-%d")
    return None


class MeetingSummariser:
    def __init__(self, source_label: str = "meeting"):
        self.source_label = source_label
        self.parser = PydanticOutputParser(pydantic_object=MeetingResponse)
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are an assistant that processes meeting transcripts.

            ### Step 1: Provide a short summary (2–3 sentences max).

            ### Step 2: List key discussion points as bullet points.

            ### Step 3: Extract ONLY action items for the participant "Kavya":
            - Each task must be actionable (something Kavya must do).
            - Assign a priority (HIGH, MED, LOW).
            - Detect deadlines: include in due_raw, and also try to normalize to YYYY-MM-DD in due_date.
            - If no deadline, leave due_raw and due_date as null.

            Transcript: {transcript}
            {format_instructions}
            """
        )
        self.chain = self.prompt | get_llm() | self.parser

    def run(self, path: str = "data/sample_transcript.txt"):
        logs, summaries, all_tasks = [], [], []
        if not os.path.exists(path):
            return {"summary": "", "discussion": [], "tasks": [], "logs": [f"Transcript not found: {path}"]}

        with open(path, "r", encoding="utf-8") as f:
            transcript = f.read().strip()

        try:
            result: MeetingResponse = self.chain.invoke({
                "transcript": transcript,
                "format_instructions": self.parser.get_format_instructions()
            })

            # store main summary
            summaries.append(result.summary)

            # process tasks
            for idx, t in enumerate(result.tasks):
                due_date = normalize_due(t.due_raw)
                all_tasks.append({
                    "id": f"mt_{idx}",
                    "title": t.title,
                    "source": self.source_label,
                    "priority": t.priority,
                    "due_raw": t.due_raw,
                    "due_date": due_date,
                    "estimate_min": None,
                    "status": "PENDING",
                    "confidence": 0.85,  # default confidence for meeting tasks
                })

            logs.append(f"Processed meeting transcript → {len(result.tasks)} tasks for Kavya")
            return {
                "summary": result.summary,
                "discussion": result.discussion_points,
                "tasks": all_tasks,
                "logs": logs,
            }
        except Exception as e:
            return {"summary": "", "discussion": [], "tasks": [], "logs": [f"ERROR: {e}"]}