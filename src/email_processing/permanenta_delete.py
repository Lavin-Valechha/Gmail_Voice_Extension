import sys
import os
import speech_recognition as sr
import pyttsx3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.gmail_auth import authenticate_gmail  # Import authentication function
from src.speech_processing.voice_assistant import VoiceAssistant  # ✅ Import VoiceAssistant

class PermanentEmailDeleter:
    def __init__(self):
        """Initialize and authenticate Gmail service."""
        creds = authenticate_gmail()
        self.service = build("gmail", "v1", credentials=creds)

        # ✅ Initialize Voice Assistant
        self.assistant = VoiceAssistant()

    def search_email_perma(self, query):
        """Search for an email using a query and return the email ID and details."""
        try:
            response = self.service.users().messages().list(userId="me", q=query).execute()
            messages = response.get("messages", [])

            if not messages:
                self.assistant.speak("No emails found matching the query.")
                return None, None

            email_id = messages[0]["id"]  # Get the first matching email

            # ✅ Fetch full email details
            email_details = self.service.users().messages().get(userId="me", id=email_id).execute()
            headers = email_details["payload"]["headers"]
            
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            snippet = email_details.get("snippet", "No preview available")

            email_info = f"📩 **Email Found:**\n📝 Subject: {subject}\n📤 Sender: {sender}\n📜 Snippet: {snippet}"
            print(email_info)
            self.assistant.speak(f"I found an email from {sender}, subject: {subject}. The message preview is {snippet}.")
            
            return email_id, email_info

        except Exception as e:
            self.assistant.speak(f"Error searching email: {str(e)}")
            return None, None

    def delete_email_perma(self, email_id):
        """Move an email to delete permanently (hard delete)."""
        try:
            self.service.users().messages().delete(userId="me", id=email_id).execute()
            self.assistant.speak(f"Email has been permanently deleted.")
            print("✅ Email deleted successfully!")
            return True
        except Exception as e:
            self.assistant.speak(f"Error deleting email: {str(e)}")
            return False


# ✅ MAIN FUNCTION WITH VOICE
if __name__ == "__main__":
    gmail_service = PermanentEmailDeleter()

    gmail_service.assistant.speak("What email do you want to delete? Say the subject, sender, or keywords.")
    query = gmail_service.assistant.listen()

    if query:
        email_id, email_info = gmail_service.search_email_perma(query)

        if email_id:
            gmail_service.assistant.speak("Are you sure you want to delete this email? Say yes or no.")
            confirmation = gmail_service.assistant.listen()

            if "yes" in confirmation:
                gmail_service.delete_email_perma(email_id)
            else:
                gmail_service.assistant.speak("Email deletion canceled.")
