import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.speech_processing.voice_assistant import VoiceAssistant  # ✅ Import VoiceAssistant
import inflect  # ✅ Converts spoken numbers to digits
import base64
from googleapiclient.discovery import build
from bs4 import BeautifulSoup  # ✅ Cleans HTML email content

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.gmail_auth import authenticate_gmail  # ✅ Import authentication function

class EmailLabelManager:
    def __init__(self):
        """Initialize Gmail API service and voice assistant."""
        self.service = build("gmail", "v1", credentials=authenticate_gmail())
        self.assistant = VoiceAssistant()  # ✅ Use VoiceAssistant for voice input
        self.inflect_engine = inflect.engine()  # ✅ Converts words to numbers

    def get_email_ids_by_label(self, label, max_results=10):
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

    def modify_email_labels(self, email_id, add_labels=None, remove_labels=None):
        """Modify labels of an email (Archive, Move, etc.)."""
        try:
            body = {
                "addLabelIds": add_labels if add_labels else [],
                "removeLabelIds": remove_labels if remove_labels else [],
            }

            self.service.users().messages().modify(
                userId="me", id=email_id, body=body
            ).execute()

            self.assistant.speak(f"Email {email_id} modified successfully!")
        except Exception as e:
            self.assistant.speak(f"Error modifying email {email_id}: {str(e)}")

    def archive_email(self, email_id):
        """Archive an email by removing it from the Inbox."""
        self.modify_email_labels(email_id, remove_labels=["INBOX"])

    def move_email_to_label(self, email_id, new_label):
        """Move an email to a specific label."""
        self.modify_email_labels(email_id, add_labels=[new_label], remove_labels=["INBOX"])


# ✅ MAIN FUNCTION WITH VOICE
if __name__ == "__main__":
    manager = EmailLabelManager()

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

    manager.assistant.speak("Which label do you want to check? Say a number between one and fourteen, Or Say 'exit' ")
    label_number = manager.assistant.listen()

    if label_number in LABELS:  
        selected_label = LABELS[label_number]
    elif "exit" in label_number:
        print("Exiting Program")
        sys.exit()
    else:
        manager.assistant.speak("Invalid label selection. Please try again.")
        sys.exit()

    manager.assistant.speak(f"Fetching emails from {selected_label}.")

    # ✅ Fetch Emails
    email_ids = manager.get_email_ids_by_label(selected_label, max_results=10)

    if email_ids:
        manager.assistant.speak(f"I found {len(email_ids)} emails in {selected_label}. Here are the details.")

        for index, email_id in enumerate(email_ids, start=1):
            email_details = manager.get_email_details(email_id)
            if email_details:
                print(f"📩 **Email {index} Details:**")
                print(f"📝 Subject: {email_details['subject']}")
                print(f"📤 Sender: {email_details['sender']}")
                print(f"📜 Body:\n{email_details['body'][:500]}...")
                print("-" * 50)

                manager.assistant.speak(f"Email {index}, Subject: {email_details['subject']}, Sender: {email_details['sender']}.")
                manager.assistant.speak(f"Message: {email_details['body'][:200]}")

    else:
        manager.assistant.speak("No emails found in this label.")
