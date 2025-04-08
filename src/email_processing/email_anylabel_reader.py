import sys
import os
import base64
from googleapiclient.discovery import build
from bs4 import BeautifulSoup  # ✅ Clean HTML email content
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.speech_processing.voice_assistant import VoiceAssistant  # ✅ Import VoiceAssistant

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.gmail_auth import authenticate_gmail  # ✅ Import authentication function

class EmailLabelReader:
    def __init__(self):
        """Initialize Gmail API service and voice assistant."""
        self.service = build("gmail", "v1", credentials=authenticate_gmail())
        self.assistant = VoiceAssistant()  # ✅ Use VoiceAssistant instead of re-implementing

    def fetch_label_emails(self, label, max_results=10):
        """Fetch email IDs based on the given label."""
        try:
            results = self.service.users().messages().list(
                userId="me", labelIds=[label], maxResults=max_results
            ).execute()
            messages = results.get("messages", [])
            return [msg["id"] for msg in messages] if messages else None
        except Exception as e:
            self.assistant.speak(f"Error fetching emails from {label}: {str(e)}")
            return None

    def get_email_details(self, email_id):
        """Fetch email details (subject, sender, body) using email ID."""
        try:
            message = self.service.users().messages().get(userId="me", id=email_id, format="full").execute()
            payload = message.get("payload", {})
            headers = payload.get("headers", [])

            subject = sender = body = "Not found"

            # Extract subject and sender
            for header in headers:
                if header["name"] == "Subject":
                    subject = header["value"]
                if header["name"] == "From":
                    sender = header["value"]

            # Extract email body
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain":
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
                    elif part["mimeType"] == "text/html":
                        body_html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        body = BeautifulSoup(body_html, "html.parser").get_text()  # Convert HTML to plain text
                        break
            else:
                body = base64.urlsafe_b64decode(payload.get("body", {}).get("data", b"")).decode("utf-8")

            return {"subject": subject, "sender": sender, "body": body}

        except Exception as e:
            self.assistant.speak(f"Error fetching email details: {str(e)}")
            return None

# ✅ MAIN FUNCTION WITH VOICE
if __name__ == "__main__":
    reader = EmailLabelReader()

    # ✅ Available Labels (Mapped to Numbers)
    LABELS = {
        "inbox": "INBOX",
        "starred": "STARRED",
        "snoozed": "SNOOZED",
        "sent": "SENT",
        "draft": "DRAFT",
        "important": "IMPORTANT",
        "trash": "TRASH",
        "spam": "SPAM",
        "scheduled": "SCHEDULED",
        "all mail": "ALL MAIL",
        "social": "CATEGORY_SOCIAL",
        "updates": "CATEGORY_UPDATES",
        "forums": "CATEGORY_FORUMS",
        "promotions": "CATEGORY_PROMOTIONS",
    }

    # ✅ Display and Speak Available Labels
    print("\n📌 **Available Labels:**")
    for key, label in LABELS.items():
        print(f"{key}. {label}")

    reader.assistant.speak("Here are the available labels. Say the number of the label you want to check.")

    # ✅ Get Label Choice via Voice
    label_number = reader.assistant.listen()

    if label_number in LABELS:
        selected_label = LABELS[label_number]
    else:
        reader.assistant.speak("Invalid label selection. Please try again.")
        sys.exit()

    reader.assistant.speak(f"Fetching emails from {selected_label}.")

    # ✅ Fetch Emails
    email_ids = reader.fetch_label_emails(selected_label, max_results=10)

    if email_ids:
        reader.assistant.speak(f"I found {len(email_ids)} emails in {selected_label}. Here are the details.")

        for index, email_id in enumerate(email_ids, start=1):
            email_details = reader.get_email_details(email_id)
            if email_details:
                print(f"📩 **Email {index} Details:**")
                print(f"📝 Subject: {email_details['subject']}")
                print(f"📤 Sender: {email_details['sender']}")
                print(f"📜 Body:\n{email_details['body'][:500]}...")
                print("-" * 50)

                reader.assistant.speak(f"Email {index}, Subject: {email_details['subject']}, Sender: {email_details['sender']}.")
                reader.assistant.speak(f"Message: {email_details['body'][:200]}")

    else:
        reader.assistant.speak("No emails found in this label.")
