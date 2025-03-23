import sys
import os
import whisper
import pyttsx3
import speech_recognition as sr
from googleapiclient.discovery import build  # ✅ Import build
from src.utils.gmail_auth import authenticate_gmail  # ✅ Import authentication function

class GmailService:
    def __init__(self):
        """Initialize and authenticate Gmail service."""
        creds = authenticate_gmail()  # Get credentials
        self.service = build("gmail", "v1", credentials=creds)  # ✅ Build service once

        # ✅ Initialize Whisper & Text-to-Speech
        self.whisper_model = whisper.load_model("small")  # Use "tiny", "base", "medium", or "large"
        self.engine = pyttsx3.init()

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Capture voice input and convert to text using Whisper."""
        with sr.Microphone() as source:
            print("🎤 Listening... Speak now.")
            self.speak("Listening, please speak now.")
            audio = sr.Recognizer().listen(source)  # ✅ Record voice input

        # ✅ Save and transcribe with Whisper
        with open("temp_audio.wav", "wb") as f:
            f.write(audio.get_wav_data())

        result = self.whisper_model.transcribe("temp_audio.wav")
        command = result["text"].strip().lower()
        print(f"🗣 You said: {command}")
        return command

    def search_email(self, query):
        """Search for an email using a query and return email ID and details."""
        try:
            response = self.service.users().messages().list(userId="me", q=query).execute()
            messages = response.get("messages", [])

            if not messages:
                self.speak("No emails found matching your query.")
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
            self.speak(f"Error searching email: {str(e)}")
            return None, None

    def delete_email(self, email_id):
        """Move an email to trash (soft delete)."""
        try:
            self.service.users().messages().trash(userId="me", id=email_id).execute()
            self.speak(f"Email has been moved to trash.")
            print("✅ Email deleted successfully!")
            return True
        except Exception as e:
            self.speak(f"Error deleting email: {str(e)}")
            return False


# ✅ MAIN FUNCTION WITH VOICE
if __name__ == "__main__":
    gmail_service = GmailService()

    gmail_service.speak("What email do you want to delete? Say the subject, sender, or keywords.")
    query = gmail_service.listen()

    if query:
        email_id, email_info = gmail_service.search_email(query)

        if email_id:
            gmail_service.speak("Are you sure you want to delete this email? Say yes or no.")
            confirmation = gmail_service.listen()

            if "yes" in confirmation:
                gmail_service.delete_email(email_id)
            else:
                gmail_service.speak("Email deletion canceled.")
