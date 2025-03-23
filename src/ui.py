import tkinter as tk
from threading import Thread
from src.speech_processing.wake_word import WakeWordDetector

class VoiceAssistantUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Assistant")

        self.status_label = tk.Label(self.root, text="Waiting for 'Hey Assistant'...", font=("Arial", 14))
        self.status_label.pack(pady=20)

        self.logs = tk.Text(self.root, height=10, width=50)
        self.logs.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Stop Listening", command=self.stop_listening)
        self.stop_button.pack(pady=5)

        self.listening = False

    def start_listening(self):
        self.listening = True
        self.logs.insert(tk.END, "Listening started...\n")
        Thread(target=self.run_wake_word).start()

    def stop_listening(self):
        self.listening = False
        self.logs.insert(tk.END, "Listening stopped.\n")

    def run_wake_word(self):
        detector = WakeWordDetector()
        detector.listen()

    def run(self):
        self.root.mainloop()
