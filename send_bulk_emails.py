import pandas as pd
import base64
import os
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ================= CONFIG =================
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

CONTACTS_FILE = "contacts.csv"
TRACKING_FILE = "tracking.csv"

AI_RESUME = "resume_ai_ml.pdf"
DA_RESUME = "resume_data_analyst.pdf"

FOLLOWUP_DAYS = 5
DELAY_SECONDS = 60   # ✅ FINAL: 60 seconds delay
# ==========================================


# 🔐 FIXED HTML SIGNATURE (LOCKED – DO NOT MODIFY)
SIGNATURE_HTML = """
<br><br>
Best regards,<br>
<b>Saurabh Pandey</b><br>
📧 saurabh395p@gmail.com | 📞 +91 8840522405 |
<a href="https://www.linkedin.com/in/saurabh-pandey-39470325a/" target="_blank">LinkedIn</a> |
<a href="https://github.com/Saurabh968896" target="_blank">GitHub</a>
"""


# ---------------- Gmail Service ----------------
def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("gmail", "v1", credentials=creds)


# ---------------- Subject ----------------
def get_subject(company):
    return f"Exploring relevant opportunities at {company}"


# ---------------- Role Detection ----------------
def detect_role(title):
    title = title.lower()
    ai_keywords = [
        "ai", "ml", "machine learning", "deep learning",
        "data scientist", "llm", "genai", "ai engineer"
    ]
    for kw in ai_keywords:
        if kw in title:
            return "AI_ML"
    return "DATA"


# ---------------- Resume Selector ----------------
def select_resume(role):
    return AI_RESUME if role == "AI_ML" else DA_RESUME


# ---------------- Email Body (HTML) ----------------
def generate_email_body(name, title, company, role):
    if role == "AI_ML":
        return f"""
<p>Hi {name},</p>

<p>
I hope you’re doing well. I noticed your role as {title} at {company},
particularly your involvement in AI-focused initiatives.
</p>

<p>
I am a PG-DBDA 2025 graduate with approximately 1.5 years of experience working
in analyst roles, along with hands-on experience in machine learning, deep learning,
and applied AI through projects and practical implementations.
</p>

<p>
I am currently exploring AI/ML roles or internships where I can contribute to
real-world projects. I’ve attached my AI/ML-focused resume for your reference.
I would also be open to data analyst roles if there are relevant opportunities
aligned with analytics-driven teams.
</p>

<p>
You can also review my GitHub profile to see my project work, and I’ve shared my
professional experience and projects on LinkedIn as well.
</p>
"""
    else:
        return f"""
<p>Hi {name},</p>

<p>
Hope you’re doing well. I noticed your role as {title} at {company}.
</p>

<p>
I am a PG-DBDA 2025 graduate with approximately 1.5 years of experience in analyst roles,
with hands-on work in data analysis, SQL, Python, and business analytics.
</p>

<p>
I am currently exploring data analyst or analytics-focused opportunities where I can
support data-driven decision-making. I’ve attached my data analyst resume for reference.
I am also actively building skills in AI/ML and would be open to relevant entry-level
opportunities in that space if applicable.
</p>

<p>
You can also check my GitHub profile to review my project work, and my LinkedIn profile
highlights my experience and projects in more detail.
</p>
"""


# ---------------- Follow-up Body ----------------
def followup_body(name):
    return f"""
<p>Hi {name},</p>

<p>
Just following up on my previous message in case it got missed.
</p>

<p>
I’d be happy to share any additional details or discuss potential opportunities, if relevant.
</p>
"""


# ---------------- Email Sender ----------------
def send_email(service, to_email, subject, body_html, resume_path=None):
    message = MIMEMultipart()
    message["to"] = to_email
    message["from"] = "me"
    message["subject"] = subject

    message.attach(MIMEText(body_html + SIGNATURE_HTML, "html"))

    if resume_path:
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(resume_path)}"'
        )
        message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()


# ---------------- Main Agent Loop ----------------
def main():
    contacts = pd.read_csv(CONTACTS_FILE)
    tracking = pd.read_csv(TRACKING_FILE)
    service = get_gmail_service()

    today = datetime.now()

    for _, row in contacts.iterrows():
        email = row["Email"]
        name = row["Name"]
        title = row["Title"]
        company = row["Company"]

        record = tracking[tracking["Email"] == email]

        # -------- INITIAL EMAIL --------
        if record.empty:
            role = detect_role(title)
            resume = select_resume(role)
            body = generate_email_body(name, title, company, role)

            send_email(
                service,
                email,
                get_subject(company),
                body,
                resume
            )

            tracking.loc[len(tracking)] = [
                email,
                "INITIAL_SENT",
                today.strftime("%Y-%m-%d"),
                "NO"
            ]

            print(f"📨 Initial email sent → {email}")
            time.sleep(DELAY_SECONDS)

        # -------- FOLLOW-UP --------
        else:
            last_sent = datetime.strptime(
                record.iloc[0]["LastSentDate"], "%Y-%m-%d"
            )
            followup_sent = record.iloc[0]["FollowUpSent"]

            if (today - last_sent).days >= FOLLOWUP_DAYS and followup_sent == "NO":
                body = followup_body(name)

                send_email(
                    service,
                    email,
                    "Following up",
                    body
                )

                tracking.loc[tracking["Email"] == email, "FollowUpSent"] = "YES"
                tracking.loc[tracking["Email"] == email, "LastSentDate"] = today.strftime("%Y-%m-%d")

                print(f"🔁 Follow-up sent → {email}")
                time.sleep(DELAY_SECONDS)

    tracking.to_csv(TRACKING_FILE, index=False)
    print("\n🎯 Agent run completed safely.")


if __name__ == "__main__":
    main()
