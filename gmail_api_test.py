from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_console()

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def send_test_email():
    service = get_gmail_service()

    message = MIMEText("This is a TEST email sent using Gmail API + Python.")
    message["to"] = "saurabhp395@gmail.com"
    message["from"] = "me"
    message["subject"] = "Gmail API Test – Success"

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"raw": raw}

    service.users().messages().send(userId="me", body=body).execute()
    print("✅ Test email sent successfully via Gmail API")

send_test_email()
