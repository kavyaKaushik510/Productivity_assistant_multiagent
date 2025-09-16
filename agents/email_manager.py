from langchain_core.output_parsers import PydanticOutputParser
from agents.schemas import Summary, Task, EmailResponse
from langchain_core.prompts import ChatPromptTemplate
from tools.llm import get_llm
from tools.gmail_provider import fetch_emails
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
            You are an AI assistant that extracts actionable tasks from emails.

            Definition: Actionable Task  
            An actionable task is a specific action the user can directly perform.  
            It should be:  
            - Concrete - clearly describes what to do (e.g., "Submit the report", "Join the Zoom call at 2pm").  
            - Executable - something the user can realistically take action on.  
            - Not vague - avoid tasks like "Read this email" or "Consider this information".  

            Step 1: Classify the email into one of:
            - PROMO - advertisements, discounts, newsletters, marketing offers  
            - ALERT - security notices, account/billing issues, urgent system messages  
            - MEETING - invites, reminders, or calendar notifications  
            - PROJECT - work, school, or team updates with clear requests or assignments  
            - OTHER - anything else (forums, digests, social updates, general FYI)

            Step 2: Rules
            - PROMO - set summary = "" and tasks = [].  
            - OTHER - return a short summary but no tasks.  
            - ALERT, MEETING, PROJECT - return both:  
                - A short summary of the email.  
                - A list of actionable tasks (see definition above)

            Step 3: Deadlines
            - Detect explicit time references (e.g., "today", "tomorrow", "by Friday", "Sept 20").  
            - Place the exact phrase in due_raw.  
            - If possible, convert it into an ISO date YYYY-MM-DD (relative to today) in due_date.  
            - If no deadline is mentioned, set both to null.

            EMAIL: {email}
            {format_instructions}
            """
        )
        self.chain = self.prompt | get_llm() | self.parser

    def run(self, n: int = 5):
        logs, summaries, all_tasks = [], [], []
        try:
            emails = fetch_emails(n)
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
                    priority="MED",   # will be updated later
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