import sys
import os
import threading
import tkinter as tk
from tkinter import scrolledtext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.main import VoiceDesktopAssistant  # Import the assistant class

class AssistantUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("500x600")
        self.assistant = VoiceDesktopAssistant()
        self.running = False

        # Title Label
        self.label = tk.Label(root, text="Voice Assistant", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(root, text="Status: Idle", font=("Arial", 12))
        self.status_label.pack()

        # Log Output Box
        self.log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=("Arial", 10))
        self.log_box.pack(pady=10)
        self.log_box.insert(tk.END, "Welcome to Voice Assistant!\n")

        # Start Button
        self.start_button = tk.Button(root, text="Start Assistant", font=("Arial", 12), bg="green", fg="white", command=self.start_assistant)
        self.start_button.pack(pady=5)

        # Stop Button
        self.stop_button = tk.Button(root, text="Stop Assistant", font=("Arial", 12), bg="red", fg="white", command=self.stop_assistant, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def start_assistant(self):
        if not self.running:
            self.running = True
            self.log("Assistant started. Listening for wake word...")
            self.status_label.config(text="Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.assistant.run, daemon=True).start()

    def stop_assistant(self):
        if self.running:
            self.running = False
            self.log("Stopping Assistant...")
            self.status_label.config(text="Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.assistant.running = False  # Stops the loop in the assistant

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    ui = AssistantUI(root)
    root.mainloop()
