import pvporcupine
import pyaudio
import struct
from src.assistant import VoiceAssistant

class WakeWordDetector:
    def __init__(self):
        self.porcupine = pvporcupine.create(keywords=["hey assistant"])
        self.assistant = VoiceAssistant()

    def listen(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=self.porcupine.sample_rate,
                         input=True, frames_per_buffer=self.porcupine.frame_length)

        while True:
            pcm = stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            keyword_index = self.porcupine.process(pcm)
            if keyword_index >= 0:
                self.assistant.handle_command()
