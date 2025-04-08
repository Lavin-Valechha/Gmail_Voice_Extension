import sys
import os
from googleapiclient.discovery import build  # ✅ Import build
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.gmail_auth import authenticate_gmail  # ✅ Import authentication function
from src.speech_processing.voice_assistant import VoiceAssistant  # ✅ Import VoiceAssistant

class TrashEmailDeleter:
    def __init__(self):
        """Initialize and authenticate Gmail service."""
        creds = authenticate_gmail()  # Get credentials
        self.service = build("gmail", "v1", credentials=creds)  # ✅ Build service once
        self.assistant = VoiceAssistant()  # ✅ Use VoiceAssistant for voice input

    def search_email(self, query):
        """Search for an email using a query and return email ID and details."""
        try:
            response = self.service.users().messages().list(userId="me", q=query).execute()
            messages = response.get("messages", [])

            if not messages:
                self.assistant.speak("No emails found matching your query.")
                return None, None

            email_id = messages[0]["id"]  # ✅ Get first matching email

            # ✅ Fetch email details
            email_details = self.service.users().messages().get(userId="me", id=email_id).execute()
            headers = email_details["payload"]["headers"]
            
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            snippet = email_details.get("snippet", "No preview available")

            email_info = f"📩 **Email Found:**\n📝 Subject: {subject}\n📤 Sender: {sender}\n📜 Snippet: {snippet}"
            print(email_info)
            
            return email_id, email_info

        except Exception as e:
            self.assistant.speak(f"Error searching email: {str(e)}")
            return None, None

    def delete_email_trash(self, email_id):
        """Move an email to trash (soft delete)."""
        try:
            self.service.users().messages().trash(userId="me", id=email_id).execute()
            self.assistant.speak(f"Email has been moved to trash.")
            print("✅ Email deleted successfully!")
            return True
        except Exception as e:
            self.assistant.speak(f"Error deleting email: {str(e)}")
            return False


# ✅ MAIN FUNCTION WITH VOICE
if __name__ == "__main__":
    gmail_service = TrashEmailDeleter()

    gmail_service.assistant.speak("What email do you want to delete? Say the subject, sender, or keywords.")
    query = gmail_service.assistant.listen()

    if query:
        email_id, email_info = gmail_service.search_email(query)

        if email_id:
            gmail_service.assistant.speak("Are you sure you want to delete this email? Say yes or no.")
            confirmation = gmail_service.assistant.listen()

            if "yes" in confirmation:
                gmail_service.delete_email_trash(email_id)
            else:
                gmail_service.assistant.speak("Email deletion canceled.")
