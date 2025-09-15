import imaplib
import email
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_emails(limit: int = 5) -> List[Dict]:
    """Fetch the most recent emails from Gmail Primary inbox using IMAP."""
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not user or not password:
        raise RuntimeError("EMAIL_USER and EMAIL_PASS must be set in .env")

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, password)
    imap.select("inbox")

    status, data = imap.search(None, 'X-GM-RAW "category:primary"')
    if status != "OK":
        raise RuntimeError("Failed to search mailbox")

    mail_ids = data[0].split()[-limit:]
    emails = []

    for mid in mail_ids:
        status, msg_data = imap.fetch(mid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
                elif content_type == "text/html" and not body:
                    # fallback if no plain text
                    body = part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        emails.append({
            "id": mid.decode(),
            "from": msg.get("From"),
            "to": msg.get("To"),
            "subject": msg.get("Subject"),
            "body": body.strip()
        })

    imap.logout()
    return emails


if __name__ == "__main__":
    # Quick smoke test
    for m in fetch_emails(3):
        print(f"- {m['subject']} ({m['from']})")