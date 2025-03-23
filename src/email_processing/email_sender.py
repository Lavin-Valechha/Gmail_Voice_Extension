import sys
import os
import re
import base64
import whisper
import speech_recognition as sr
import pyttsx3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

# Ensure authentication function exists
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.gmail_auth import authenticate_gmail  # Ensure this function is implemented

class GmailHelper:
    def __init__(self):
        self.service = build("gmail", "v1", credentials=authenticate_gmail())
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model("small")  # Change to "medium" or "large" for better accuracy
        self.engine = pyttsx3.init()

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Capture voice input and transcribe it using Whisper."""
        with sr.Microphone() as source:
            print("🎤 Listening... Speak now.")
            self.speak("Listening, please speak now.")
            audio = self.recognizer.listen(source)

        # Save audio and transcribe with Whisper
        with open("temp_audio.wav", "wb") as f:
            f.write(audio.get_wav_data())

        result = self.whisper_model.transcribe("temp_audio.wav")
        command = result["text"].strip().lower()
        print(f"🗣 You said: {command}")
        return command

    def format_email_body(self, text):
        """Convert markdown-like formatting to HTML."""
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)  # **Bold**
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)  # *Italic*
        text = re.sub(r"_(.*?)_", r"<u>\1</u>", text)  # _Underline_
        text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)  # `Code`
        text = text.replace("\n", "<br>")  # Convert new lines to <br>
        return text

    def send_email(self, to_email, subject, message_body):
        """Sends an email via Gmail API."""
        # ✅ Fix email format
        to_email = to_email.replace(" at ", "@")  # Convert 'at' to '@'
        to_email = to_email.replace(" ", "")  # Remove spaces
        if "@" not in to_email:
                to_email += "@gmail.com"  # Default to Gmail

        try:
            if "@gmail.com" not in to_email:
                to_email += "@gmail.com"

            formatted_body = self.format_email_body(message_body)
            message = MIMEText(formatted_body, "html")
            message["to"] = to_email
            message["subject"] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message = self.service.users().messages().send(
                userId="me", body={"raw": raw_message}
            ).execute()

            print(f"✅ Email sent successfully to {to_email}. Message ID: {send_message['id']}")
            self.speak(f"Email sent successfully to {to_email}.")
            return send_message
        except HttpError as error:
            print(f"❌ An error occurred: {error}")
            self.speak("An error occurred while sending the email.")
            return None

    def read_latest_emails(self, max_results=5):
        """Reads the latest emails from the inbox."""
        try:
            results = self.service.users().messages().list(userId="me", maxResults=max_results).execute()
            messages = results.get("messages", [])

            if not messages:
                print("📭 No emails found.")
                self.speak("No emails found.")
                return []

            emails = []
            for msg in messages:
                msg_data = self.service.users().messages().get(userId="me", id=msg["id"]).execute()
                snippet = msg_data.get("snippet", "No content")
                emails.append(snippet)

            for idx, email in enumerate(emails, 1):
                print(f"{idx}. {email}")
                self.speak(f"Email {idx}: {email}")

            return emails
        except HttpError as error:
            print(f"❌ An error occurred while reading emails: {error}")
            self.speak("An error occurred while reading emails.")
            return []

if __name__ == "__main__":
    helper = GmailHelper()

    while True:
        print("\nSay a command: 'Send email', 'Read emails', or 'Exit'.")
        helper.speak("Say a command: Send email, Read emails, or Exit.")
        command = helper.listen()

        if "send email" in command:
            helper.speak("Who do you want to send the email to?")
            to_email = helper.listen()

            helper.speak("What is the subject of the email?")
            subject = helper.listen()

            helper.speak("What is the message?")
            message_body = helper.listen()

            helper.send_email(to_email, subject, message_body)

        elif "read emails" in command:
            helper.read_latest_emails()

        elif "exit" in command:
            print("👋 Exiting the program.")
            helper.speak("Exiting the program.")
            break

        else:
            print("❌ Invalid command. Please try again.")
            helper.speak("Invalid command. Please try again.")
