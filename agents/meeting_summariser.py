# agents/meeting_summariser.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from tools.llm import get_llm
from tools.docs_provider import fetch_doc_text
from agents.schemas import MeetingResponse


class MeetingSummariser:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=MeetingResponse)

        self.prompt = ChatPromptTemplate.from_template(
            """
            You are an assistant that summarises meeting notes and extracts
            actionable items for user: Kavya.

            Step 1: Provide a concise summary of the meeting.
            Step 2: Extract key discussion points as bullet points.
            Step 3: Extract ONLY action items assigned to Kavya.
            - Each task should have a clear priority: HIGH, MED, or LOW.
            - If there are due dates mentioned ("by Friday"), include them in due_raw.

            MEETING NOTES:
            {notes}

            {format_instructions}
            """
        )

        self.chain = self.prompt | get_llm() | self.parser

    def run(self, doc_id: str) -> MeetingResponse:
        notes = fetch_doc_text(doc_id)
        return self.chain.invoke(
            {
                "notes": notes,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )
