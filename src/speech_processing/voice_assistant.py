import whisper
import pyttsx3
import speech_recognition as sr
import keyboard  # ✅ Allows stopping via keyboard
import inflect

class VoiceAssistant:
    def __init__(self):
        """Initialize voice processing modules."""
        self.whisper_model = whisper.load_model("small")
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.inflect_engine = inflect.engine()  # ✅ Converts words to numbers
        self.running = True  # ✅ Used to handle stop command
        # ✅ Set up stop command (Press 'ESC' to exit)
        keyboard.add_hotkey("esc", self.stop_assistant)

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Capture voice input and convert to text using Whisper."""
        with sr.Microphone() as source:
            print("🎤 Listening... Speak now.")
            self.speak("Listening, please speak now.")
            audio = self.recognizer.listen(source)

        # ✅ Save recorded audio to a file
        with open("temp_audio.wav", "wb") as f:
            f.write(audio.get_wav_data())

        # ✅ Whisper processes the saved audio file
        result = self.whisper_model.transcribe("temp_audio.wav")
        command = result["text"].strip().lower()
        print(f"🗣 You said: {command}")

        # ✅ Convert spoken number words to digits
        words = command.split()
        for i, word in enumerate(words):
            num = self.inflect_engine.ordinal(word)  # ✅ Convert "one" → "1"
            if num.isdigit():
                words[i] = num  # Replace word with digit

        converted_command = " ".join(words)
        print(f"🔢 Converted Command: {converted_command}")
        return converted_command

    def stop_assistant(self):
        """Stop the assistant on command."""
        print("🛑 Stopping Assistant...")
        self.speak("Stopping Assistant.")
        self.running = False