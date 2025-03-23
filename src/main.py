import sys
import os
from src.speech_processing.voice_assistant import VoiceAssistant
from src.email_processing.email_reader_specific import EmailReaderSpecific
from src.email_processing.email_sender import EmailSender
from src.email_processing.email_delete import EmailDeleter
from src.email_processing.email_anylabel_reader import GmailLabelReader
from src.email_processing.email_archive_move_any import GmailLabelManager
from src.email_processing.permanenta_delete import PermanentEmailDeleter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class VoiceDesktopAssistant:
    def __init__(self):
        """Initialize Voice Assistant and Email Features."""
        self.assistant = VoiceAssistant()
        self.email_reader = EmailReaderSpecific()
        self.email_sender = EmailSender()
        self.email_deleter = EmailDeleter()
        self.label_reader = GmailLabelReader()
        self.label_manager = GmailLabelManager()
        self.permanent_deleter = PermanentEmailDeleter()
        self.running = True
    
    def process_command(self, command):
        """Process user commands and call appropriate functions."""
        if "read email" in command:
            self.assistant.speak("Reading your emails.")
            query = self.assistant.listen()
            self.email_reader.search_email_specific(query)
        
        elif "send email" in command:
            self.assistant.speak("Who do you want to send the email to?")
            recipient = self.assistant.listen()
            self.assistant.speak("What is the subject?")
            subject = self.assistant.listen()
            self.assistant.speak("What should be the message body?")
            body = self.assistant.listen()
            self.email_sender.send_email(recipient, subject, body)
        
        elif "delete email" in command:
            self.assistant.speak("Do you want to move it to trash or delete permanently?")
            choice = self.assistant.listen()
            self.assistant.speak("What is the email subject?")
            query = self.assistant.listen()
            email_id = self.email_reader.search_email_specific(query)
            if email_id:
                if "permanent" in choice:
                    self.assistant.speak("Proceeding with permanent deletion.")
                    self.permanent_deleter.delete_email(email_id)
                else:
                    self.assistant.speak("Moving email to trash.")
                    self.email_deleter.delete_email(email_id)
            else:
                self.assistant.speak("No matching email found.")
        
        elif "check label" in command:
            self.assistant.speak("Which label do you want to check?")
            label = self.assistant.listen()
            self.label_reader.get_email_ids_by_label(label)
        
        elif "archive email" in command or "move email" in command:
            self.assistant.speak("What is the email subject?")
            query = self.assistant.listen()
            email_id = self.email_reader.search_email_specific(query)
            if email_id:
                self.assistant.speak("Which label should it be moved to?")
                new_label = self.assistant.listen()
                self.label_manager.move_email_to_label(email_id, new_label)
            else:
                self.assistant.speak("No matching email found.")
        
        elif "exit" in command or "stop" in command:
            self.assistant.speak("Stopping assistant.")
            self.running = False
        
        else:
            self.assistant.speak("I didn't understand. Please try again.")
    
    def run(self):
        """Main loop for wake word and command processing."""
        self.assistant.speak("Hello! Say 'Hey Assistant' or press Enter to start.")

        while self.running:
            wake_word = input("Press Enter to start or say 'Hey Assistant': ")
            if wake_word.lower() == "hey assistant" or wake_word == "":
                self.assistant.speak("How can I assist you?")
                command = self.assistant.listen()
                self.process_command(command)
        
        print("✅ Assistant has stopped.")

if __name__ == "__main__":
    assistant = VoiceDesktopAssistant()
    assistant.run()