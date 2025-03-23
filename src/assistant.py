from src.speech_processing.speech_to_text import recognize_speech
from src.speech_processing.text_to_speech import speak
from src.email_processing.email_manager import EmailManager

class VoiceAssistant:
    def __init__(self):
        self.email_manager = EmailManager()

    def handle_command(self, command):
        if "send email" in command:
            speak("Who do you want to email?")
            recipient = recognize_speech()
            
            speak("What is the subject?")
            subject = recognize_speech()
            
            speak("What is the message?")
            body = recognize_speech()

            response = self.email_manager.send_email(recipient, subject, body)
            speak(response)
