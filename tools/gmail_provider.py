import imaplib
import email
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_gmail_imap(n: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch last N emails from Gmail inbox using IMAP.
    Returns list of dicts: {id, from, to, subject, body}.
    """
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not user or not password:
        raise ValueError("Set EMAIL_USER and EMAIL_PASS in .env")

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, password)
    imap.select("inbox")

    status, messages = imap.search(None, 'X-GM-RAW "category:primary"')
    mail_ids = messages[0].split()[-n:]  # get last n emails

    emails = []
    for mid in mail_ids:
        status, msg_data = imap.fetch(mid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
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
    mails = fetch_gmail_imap(3)
    for m in mails:
        print(f"- {m['subject']} ({m['from']})")
