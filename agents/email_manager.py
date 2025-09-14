from langchain_core.output_parsers import PydanticOutputParser
from agents.schemas import EmailResponse
from langchain_core.prompts import ChatPromptTemplate
from tools.llm import get_llm
from tools.gmail_provider import fetch_gmail_imap
import dateparser


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
        # Prompt: classify + extract deadlines
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are an assistant that extracts ONLY actionable tasks from emails.

            ### Step 1: Classify the email into one of:
            - PROMO → advertisements, discounts, newsletters, offers
            - ALERT → security, account, billing, urgent system messages
            - MEETING → invites, reminders, calendar notifications
            - PROJECT → work, school, team updates, assignments, direct action requests
            - OTHER → anything else (forums, digests, social, FYI)

            ### Step 2: Rules
            - If category is PROMO → set summary to "" (empty string) and tasks to [].
            - If category is OTHER → return a short summary, but no tasks.
            - If category is ALERT, MEETING, or PROJECT → return a short summary and actionable tasks.
            - Each task MUST be something the user can/should do (e.g., "Reset password", "Join Zoom call at 2pm").
            - Do not invent vague tasks like "Read this email" or "Consider the information".

            ### Step 3: Deadlines
            - Detect explicit deadlines ("today", "tomorrow", "by Friday", "Sept 20").
            - Put the original phrase into due_raw.
            - If possible, also output due_date in YYYY-MM-DD format relative to today.
            - If no explicit deadline → leave due_raw and due_date as null.

            EMAIL: {email}
            {format_instructions}
            """
        )
        self.chain = self.prompt | get_llm() | self.parser

    def run(self, n: int = 3):
        logs, summaries, all_tasks = [], [], []
        try:
            emails = fetch_gmail_imap(n)
            logs.append(f"Fetched {len(emails)} emails from Gmail.")
        except Exception as e:
            return {"summaries": [], "tasks": [], "logs": [f"ERROR: Gmail fetch failed - {e}"]}

        for em in emails:
            try:
                email_text = f"Subject: {em['subject']}\n\n{em['body']}"
                result: EmailResponse = self.chain.invoke({
                    "email": email_text,
                    "format_instructions": self.parser.get_format_instructions()
                })

                if result.category == "PROMO":
                    logs.append(f"Ignored PROMO email: '{em['subject']}'")
                    continue

                summaries.append(f"[{em['subject']}] ({result.category}) {result.summary}")

                for idx, t in enumerate(result.tasks):
                    due_date = normalize_due(t.due_raw)
                    all_tasks.append({
                        "id": f"{em['id']}_{idx}",
                        "title": t.title,
                        "source": self.source_label,
                        "priority": "MED",  # will be updated later in TaskPrioritizer
                        "due_raw": t.due_raw,
                        "due_date": due_date,
                        "estimate_min": None,
                        "status": "PENDING",
                        "confidence": t.confidence
                    })

                logs.append(f"Processed '{em['subject']}' → {len(result.tasks)} tasks")
            except Exception as e:
                logs.append(f"ERROR: Processing '{em['subject']}' - {e}")

        return {"summaries": summaries, "tasks": all_tasks, "logs": logs}