import sys
import os
import base64
from googleapiclient.discovery import build
import keyboard
from email.mime.text import MIMEText
from bs4 import BeautifulSoup  # ✅ To clean HTML email content
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.speech_processing.voice_assistant import VoiceAssistant  # ✅ Import VoiceAssistant

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.gmail_auth import authenticate_gmail  # ✅ Import authentication function

class EmailReaderSpecific:
    def __init__(self):
        """Initialize Gmail API service and voice assistant."""
        self.service = build("gmail", "v1", credentials=authenticate_gmail())
        self.assistant = VoiceAssistant()  # ✅ Use VoiceAssistant

    def search_email_specific(self, query, max_result=10):
        """Search for emails based on a query."""
        try:
            response = self.service.users().messages().list(userId="me", q=query, maxResults=max_result).execute()
            messages = response.get("messages", [])

            if not messages:
                self.assistant.speak("No emails found matching your query.")
                return []

            return [msg["id"] for msg in messages]  # Return list of email IDs

        except Exception as e:
            self.assistant.speak(f"Error searching email: {str(e)}")
            return []

    def get_email_details(self, email_id):
        """Fetch email details (subject, sender, body) using email ID."""
        try:
            message = self.service.users().messages().get(userId="me", id=email_id, format="full").execute()
            payload = message.get("payload", {})
            headers = payload.get("headers", [])

            subject = sender = "Not found"
            body = "No body content"

            # Extract subject and sender
            for header in headers:
                if header["name"] == "Subject":
                    subject = header["value"]
                if header["name"] == "From":
                    sender = header["value"]

            # Extract email body (text/plain or text/html)
            parts = payload.get("parts", [])
            if parts:
                for part in parts:
                    if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        break
                    elif part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                        body_html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        body = BeautifulSoup(body_html, "html.parser").get_text()  # Convert HTML to text
                        break
            elif "body" in payload and "data" in payload["body"]:
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")

            return {"subject": subject, "sender": sender, "body": body}

        except Exception as e:
            self.assistant.speak(f"Error fetching email details for ID {email_id}: {str(e)}")
            return None

# ✅ MAIN FUNCTION WITH VOICEASSISTANT
if __name__ == "__main__":
    reader = EmailReaderSpecific()

    reader.assistant.speak("What email do you want to find? Say the subject, sender, or keywords.")
    query = reader.assistant.listen()

    if query:
        email_ids = reader.search_email_specific(query, max_result=10)

        if email_ids:
            reader.assistant.speak(f"I found {len(email_ids)} matching emails. Here are the details.")
            print(f"\n✅ Found {len(email_ids)} matching emails.\n")

            for index, email_id in enumerate(email_ids, start=1):
                email_details = reader.get_email_details(email_id)
                if email_details:
                    print(f"📩 **Email {index} Details:**")
                    print(f"📝 Subject: {email_details['subject']}")
                    print(f"📤 Sender: {email_details['sender']}")
                    print(f"📜 Body:\n{email_details['body'][:500]}...")  # Show first 500 chars
                    print("-" * 50)

                    # 🔊 Speak email details
                    reader.assistant.speak(f"Email {index}, Subject: {email_details['subject']}, Sender: {email_details['sender']}.")
                    reader.assistant.speak(f"Message: {email_details['body'][:200]}")  # Speak first 200 characters

        else:
            reader.assistant.speak("No matching emails found.")
