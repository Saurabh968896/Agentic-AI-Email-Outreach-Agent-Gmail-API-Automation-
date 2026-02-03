import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_ID = os.getenv("GMAIL_ID")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

TO_EMAIL = GMAIL_ID  # send to yourself

BODY = """
Hi Saurabh,

This is a test email from your Python email agent.

If you received this, Gmail SMTP is working correctly.

Regards,
Email Agent
"""

msg = MIMEText(BODY)
msg["From"] = GMAIL_ID
msg["To"] = TO_EMAIL
msg["Subject"] = "Test Email – Python Automation"

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(GMAIL_ID, APP_PASSWORD)
    server.send_message(msg)

print("✅ Test email sent successfully")
