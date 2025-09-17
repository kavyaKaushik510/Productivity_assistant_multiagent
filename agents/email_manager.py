# agents/email_manager.py
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tools.llm import get_llm
from tools.gmail_provider import fetch_emails
from agents.schemas import Summary, Task, EmailResponse
from agents.meeting_summariser import MeetingSummariser
import dateparser, re


def normalize_due(raw: str) -> str | None:
    if not raw:
        return None
    dt = dateparser.parse(raw, settings={"PREFER_DATES_FROM": "future"})
    if dt:
        return dt.strftime("%Y-%m-%d")
    return None


class EmailManager:
    def __init__(self, source_label: str = "gmail"):
        self.source_label = source_label
        self.parser = PydanticOutputParser(pydantic_object=EmailResponse)
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are an AI assistant that extracts actionable tasks from emails.

            Definition: Actionable Task  
            - A specific action the user can directly perform.  
            - Must be concrete (e.g., "Submit the report").  
            - Skip vague tasks like "Read this email".  

            Step 1: Classify the email into exactly one category:  
            PROMO, ALERT, MEETING, PROJECT, OTHER  

            Step 2: Apply rules  
            - PROMO: marketing, ads, newsletters - summary is empty, tasks is empty  
            - OTHER: general info with no clear action - short summary only, tasks is empty  
            - ALERT: security warnings or urgent notices - include summary and the required task (e.g., reset password), include deadline if present  
            - MEETING: scheduling or meeting logistics - include summary, only add tasks if clearly assigned in the email itself (detailed notes are handled separately)  
            - PROJECT: work or academic tasks, deliverables, collaboration requests - include summary, extract each action item as a task, detect deadlines if present  

            Step 3: Deadlines  
            - For every task, always check if the email mentions time constraints.  
            - If found, you MUST fill both:  
            • due_raw = the exact phrase from the email (e.g., "by tomorrow afternoon")  
            • due_date = ISO format (YYYY-MM-DD) if it can be converted  
            - Valid examples:  
            "by tomorrow afternoon" → due_raw="by tomorrow afternoon", due_date=<tomorrows date>  
            "within 5 days" → due_raw="within 5 days", due_date=<today+5>  
            "before the 5 oclock session" → due_raw="before the 5 oclock session", due_date=<same day if resolvable>  
            - If no deadline is mentioned, leave both as null.  
            - Do not include deadlines in the summary text — they must always appear in the task fields.  


            EMAIL:  
            {email}  

            {format_instructions}  
            """
        )
        self.chain = self.prompt | get_llm() | self.parser
        self.meeting_agent = MeetingSummariser()  # added here

    def run(self, n: int = 3):
        logs, summaries, all_tasks = [], [], []
        try:
            emails = fetch_emails(n)
            logs.append(f"Fetched {len(emails)} emails from Gmail.")
        except Exception as e:
            return {"summaries": [], "tasks": [], "logs": [f"ERROR: Gmail fetch failed - {e}"]}

        for em in emails:
            try:
                email_text = f"Subject: {em['subject']}\n\n{em['body']}"

                # detect meeting notes with Google Doc link 
                doc_match = re.search(r"https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)", em["body"])
                if doc_match:
                    doc_id = doc_match.group(1)
                    logs.append(f"Detected meeting notes in '{em['subject']}' - using Google Doc {doc_id}")

                    meeting_result = self.meeting_agent.run(doc_id)

                    summaries.append(Summary(
                        subject=em["subject"],
                        category="MEETING",
                        text=meeting_result.summary
                    ))

                for idx, t in enumerate(meeting_result.tasks):
                    due_date = normalize_due(t.due_raw)
                    all_tasks.append(t.copy(update={
                        "id": f"{em['id']}_mt_{idx}",
                        "source": "meeting",
                        "due_date": due_date
                    }))

                    continue

                # Email classification
                result: EmailResponse = self.chain.invoke({
                    "email": email_text,
                    "format_instructions": self.parser.get_format_instructions()
                })

                if result.category == "PROMO":
                    logs.append(f"Ignored PROMO email: '{em['subject']}'")
                    continue

                summaries.append(Summary(
                    subject=em["subject"],
                    category=result.category,
                    text=result.summary
                ))

                for idx, t in enumerate(result.tasks):
                    due_date = normalize_due(t.due_raw)
                    all_tasks.append(Task(
                        id=f"{em['id']}_{idx}",
                        title=t.title,
                        source=self.source_label,
                        priority="MED",
                        due_raw=t.due_raw,
                        due_date=due_date,
                        estimate_min=None,
                        status="PENDING",
                        confidence=t.confidence
                    ))

                logs.append(f"Processed '{em['subject']}' - {len(result.tasks)} tasks")

            except Exception as e:
                logs.append(f"ERROR: Processing '{em['subject']}' - {e}")

        # Deduplicate tasks by title+due_date
        unique = {}
        for task in all_tasks:
            key = (task.title.strip().lower(), task.due_date)
            if key not in unique:
                unique[key] = task
        all_tasks = list(unique.values())

        return {"summaries": summaries, "tasks": all_tasks, "logs": logs}
