import sys
import os
import keyboard
import threading
import spacy  # ✅ Import spaCy for NLP

# Ensure the parent directory is added to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.speech_processing.voice_assistant import VoiceAssistant
from src.email_processing.email_reader_specific import EmailReaderSpecific
from src.email_processing.email_sender import GmailHelper
from src.email_processing.email_delete import TrashEmailDeleter
from src.email_processing.permanenta_delete import PermanentEmailDeleter
from src.email_processing.email_anylabel_reader import EmailLabelReader
from src.email_processing.email_archive_move_any import EmailLabelManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class VoiceDesktopAssistant:
    def __init__(self):
        """Initialize Voice Assistant, Email Features, and NLP Model."""
        self.assistant = VoiceAssistant()
        self.email_reader = EmailReaderSpecific()
        self.email_sender = GmailHelper()
        self.trash_deleter = TrashEmailDeleter()
        self.permanent_deleter = PermanentEmailDeleter()
        self.label_reader = EmailLabelReader()
        self.label_manager = EmailLabelManager()
        self.running = True
        self.nlp = spacy.load("en_core_web_sm")  # ✅ Load spaCy NLP model


    def get_input(self, retries=3):
    # """Get input from either voice or keyboard with retry limit."""
        if retries <= 0:
            self.assistant.speak("Input failed after retries. Please try again later.")
            return None  # Exit if retries are exhausted
    
        self.assistant.speak("You can speak or type your command.")
        print("🎤 Speak now or type below:")
    
        input_event = threading.Event()
        input_command = [None]
    
        def keyboard_listener():
            input_command[0] = input("⌨️ Type your command: ").strip().lower()
            input_event.set()
    
        keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
        keyboard_thread.start()
        
        voice_command = self.assistant.listen().strip().lower()
        
        if voice_command:
            input_event.set()
            return voice_command
        
        input_event.wait(timeout=5)
        return input_command[0] if input_command[0] else self.get_input(retries - 1)






    
    def interpret_command(self, command):
        """Process command using NLP for better understanding."""
        doc = self.nlp(command)
        
        # ✅ GREETINGS
        if any(token.text in ["hello", "hi", "hey", "good morning", "good evening"] for token in doc):
            self.assistant.speak("Hello! How can I help you today?")
            return "greeting"  # Stop execution after responding

        # ✅ READ EMAIL (Variations: read, check, show, fetch)
        if any(token.lemma_ in ["read", "check", "show", "fetch", "open"] for token in doc) and "email" in command:
            return "read email"

        # ✅ SEND EMAIL (Variations: send, compose, write, draft)
        if any(token.lemma_ in ["send", "compose", "write", "draft"] for token in doc) and "email" in command:
            return "send email"

        # ✅ DELETE EMAIL (Variations: delete, remove, erase, discard)
        if any(token.lemma_ in ["delete", "remove", "erase", "discard"] for token in doc) and "email" in command:
            return "delete email"

        # ✅ ARCHIVE/MOVE EMAIL (Variations: archive, move, organize)
        if any(token.lemma_ in ["archive", "move", "organize"] for token in doc) and "email" in command:
            return "archive email"

        # ✅ EXIT (Variations: exit, stop, quit)
        if "exit" in command or "stop" in command or "quit" in command:
            self.assistant.speak("Stopping assistant.")
            self.running = False
            return "exit"

        # ✅ UNKNOWN COMMAND HANDLING
        self.assistant.speak("I'm not sure what you mean. Can you rephrase?")
        return "unknown"
    
    def process_command(self, command):
        """Process user commands and call appropriate functions with full execution logic."""
        retry_count = 0
        while retry_count < 3:
            interpreted_command = self.interpret_command(command)
            if interpreted_command and interpreted_command != "unknown":
                break
            self.assistant.speak("I didn't understand. Can you rephrase?")
            command = self.get_input()
            retry_count += 1

        if retry_count == 3:
            self.assistant.speak("I couldn't understand your command. Please try again later.")
            return
        
        
        if interpreted_command == "read email":
            self.assistant.speak("Which label do you want to check? Say a label name clearly, or say 'exit'.")
            print("Which label do you want to check? Say a label name clearly, or say 'exit'")
            label_number = self.get_input()
            
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
            
            
            if label_number in LABELS:
                selected_label = LABELS[label_number]
                self.assistant.speak(f"Fetching emails from {selected_label}.")
                email_ids = self.label_reader.fetch_label_emails(selected_label, max_results=10)
                if email_ids:
                    for index, email_id in enumerate(email_ids, start=1):
                        # ✅ Check for 'q' key press (Keyboard Stop)
                        if keyboard.is_pressed("q"):
                            self.assistant.speak("Stopping email reading.")
                            break  # Exit the loop
                        
                        self.assistant.speak("Say 'stop' anytime to cancel.")

                        # ✅ Check for "stop" or "cancel" (Voice Stop)
                        stop_command = self.get_input()
                        if "stop" in stop_command or "cancel" in stop_command:
                            self.assistant.speak("Stopping email reading. You can give another command.")
                            return  # ✅ Ends this command cleanly, returns to run loop
                        
                        email_details = self.label_reader.get_email_details(email_id)
                        if email_details:
                            print(f"📩 **Email {index} Details:**")
                            print(f"📝 Subject: {email_details['subject']}")
                            print(f"📤 Sender: {email_details['sender']}")
                            print(f"📜 Body:\n{email_details['body'][:500]}...")
                            print("-" * 50)
                            self.assistant.speak(f"Email {index}, Subject: {email_details['subject']}, Sender: {email_details['sender']}.")
                else:
                    self.assistant.speak("No emails found in this label.")
            else:
                self.assistant.speak("Invalid label selection. Please try again.")
        
        elif interpreted_command == "send email":
            self.assistant.speak("Who do you want to send the email to?")
            print("Who do you want to send the email to")
            to_email = self.get_input()

            self.assistant.speak("What is the subject of the email?")
            print("What is the subject of the email?")
            subject = self.get_input()
            
            self.assistant.speak("What is the message?")
            print("What is the message?")
            message_body = self.get_input()

            self.email_sender.send_gmail_email(to_email, subject, message_body)
        
        elif interpreted_command == "delete email":
            self.assistant.speak("Do you want to move it to trash or delete permanently?")
            print("Do you want to move it to trash or delete permanently")
            choice = self.get_input()
            if "permanent" in choice:
                self.assistant.speak("What email do you want to delete? Say the subject, sender, or keywords.")
                query = self.get_input()
                email_id, _ = self.permanent_deleter.search_email(query)
                if email_id:
                    self.assistant.speak("Are you sure you want to delete this email? Say yes or no.")
                    confirmation = self.get_input()
                    if "yes" in confirmation:
                        self.permanent_deleter.delete_email_perma(email_id)
                    else:
                        self.assistant.speak("Email deletion canceled.")

        elif interpreted_command in ["archive email", "move mail"]:
            self.assistant.speak("Which label do you want to move an email to? Say a number between one and fourteen.")
            print("Which label do you want to move an email to? Say a number between one and fourteen.")
            label_number = self.get_input()

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

            # ✅ Check if label is valid
            if label_number in LABELS:
                selected_label = LABELS[label_number]
            elif "exit" in label_number:
                self.assistant.speak("Exiting label selection.")
                return
            else:
                self.assistant.speak("Invalid label selection. Please try again.")
                return

            # ✅ Ask which email to move
            self.assistant.speak(f"Which email do you want to move to {selected_label}? Say the subject, sender, or keywords.")
            query = self.get_input()
            email_id, _ = self.label_manager.search_email(query)

            if email_id:
                # ✅ Fetch & show email details before moving
                email_details = self.label_manager.get_email_details(email_id)
                if email_details:
                    self.assistant.speak(f"I found an email from {email_details['sender']}, subject: {email_details['subject']}. Do you want to move it?")
                    print(f"📩 **Email Found:**\n📝 Subject: {email_details['subject']}\n📤 Sender: {email_details['sender']}")
                    
                    # ✅ Ask for confirmation
                    confirmation = self.get_input()
                    if "yes" in confirmation:
                        self.label_manager.move_email_to_label(email_id, selected_label)
                        self.assistant.speak(f"Email has been moved to {selected_label}.")
                    else:
                        self.assistant.speak("Email move canceled.")
                else:
                    self.assistant.speak("Could not retrieve email details. Try again.")
            else:
                self.assistant.speak("Could not find the specified email.")

        
        elif interpreted_command == "exit":
            self.assistant.speak("Stopping assistant.")
            print("Stopping assistant.")
            self.running = False
        
        else:
            self.assistant.speak("I didn't understand. Please try again.")
    
    def run(self):
    # """Main loop for wake word and command processing."""
        self.assistant.speak("Hello! Say 'Hey Assistant' or press Enter to start.")
        while self.running:
            wake_word = input("Press Enter to start or say 'Hey Assistant': ").strip().lower()
            if wake_word in ["", "hey assistant"]:
                self.assistant.speak("How can I assist you?")
                command = self.get_input()
                if command and "back" in command.lower():  # Allow returning to wake word
                    self.assistant.speak("Returning to wake mode.")
                    continue
                if command:
                    self.process_command(command)

        print("✅ Assistant has stopped.")

if __name__ == "__main__":
    assistant = VoiceDesktopAssistant()
    assistant.run()
