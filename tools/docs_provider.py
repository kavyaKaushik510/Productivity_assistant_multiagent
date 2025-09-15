# tools/docs_provider.py
from __future__ import annotations
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
TOKEN_PATH = "secrets/docs_token.json"
CREDS_PATH = "secrets/credentials.json"


def get_docs_service():
    """Authenticate and return a Google Docs API service client."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("docs", "v1", credentials=creds)


def fetch_doc_text(doc_id: str) -> str:
    """Return full plain text from a Google Doc."""
    service = get_docs_service()
    doc = service.documents().get(documentId=doc_id).execute()

    text_chunks = []
    for c in doc.get("body", {}).get("content", []):
        if "paragraph" in c:
            for elem in c["paragraph"].get("elements", []):
                if "textRun" in elem:
                    text_chunks.append(elem["textRun"].get("content", ""))

    return "".join(text_chunks).strip()
