import sys
import os
import speech_recognition as sr
import pyttsx3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.gmail_auth import authenticate_gmail  # Import authentication function

class GmailServicePerma:
    def __init__(self):
        """Initialize and authenticate Gmail service."""
        creds = authenticate_gmail()
        self.service = build("gmail", "v1", credentials=creds)

        # ✅ Initialize Speech Recognition & Text-to-Speech
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Capture voice input and convert to text."""
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.speak("Listening, please speak now.")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            command = self.recognizer.recognize_google(audio).lower()
            print(f"🗣 You said: {command}")
            return command
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that. Please repeat.")
            return self.listen()  # 🔄 Retry if unclear
        except sr.RequestError:
            self.speak("There was a problem with the speech service.")
            return None

    def search_emailPerma(self, query):
        """Search for an email using a query and return the email ID and details."""
        try:
            response = self.service.users().messages().list(userId="me", q=query).execute()
            messages = response.get("messages", [])

            if not messages:
                self.speak("No emails found matching the query.")
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
            self.speak(f"I found an email from {sender}, subject: {subject}. The message preview is {snippet}.")
            
            return email_id, email_info

        except Exception as e:
            self.speak(f"Error searching email: {str(e)}")
            return None, None

    def delete_emailPerma(self, email_id):
        """Move an email to delete permanently (hard delete)."""
        try:
            self.service.users().messages().delete(userId="me", id=email_id).execute()
            self.speak(f"Email has been permanently deleted.")
            print("✅ Email deleted successfully!")
            return True
        except Exception as e:
            self.speak(f"Error deleting email: {str(e)}")
            return False


# ✅ MAIN FUNCTION WITH VOICE
if __name__ == "__main__":
    gmail_service = GmailServicePerma()

    gmail_service.speak("What email do you want to delete? Say the subject, sender, or keywords.")
    query = gmail_service.listen()

    if query:
        email_id, email_info = gmail_service.search_emailPerma(query)

        if email_id:
            gmail_service.speak("Are you sure you want to delete this email? Say yes or no.")
            confirmation = gmail_service.listen()

            if "yes" in confirmation:
                gmail_service.delete_emailPerma(email_id)
            else:
                gmail_service.speak("Email deletion canceled.")
