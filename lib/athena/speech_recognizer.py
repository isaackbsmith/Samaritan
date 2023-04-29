import json
import logging
import pyaudio
from pathlib import Path
from vosk import Model, KaldiRecognizer


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class SpeechRecognizer:

    def __init__(self) -> None:
        self.model_path = Path().parent.parent.joinpath("intel/speech/model")
        self.model = Model(str(self.model_path))

    def listen(self):
        logger.debug("[*] Processing speech")

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        RATE = 16000
        LISTEN_TIME = 5
        CHANNELS = 1

        stream = pyaudio.PyAudio()
        logger.debug("[*] Opening recording stream")
        audio_stream = stream.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        audio_stream.start_stream()

        recognizer = KaldiRecognizer(self.model, RATE)
        recognizer.SetWords(True)

        for _ in range(0, int(RATE / CHUNK * LISTEN_TIME)):
            while True:
                transcription = audio_stream.read(
                    44100, exception_on_overflow=False)
                if len(transcription) == 0:
                    break
                if recognizer.AcceptWaveform(transcription):
                    result = json.loads(recognizer.Result())
                    logger.debug(f"""[*] Transcribed: {result["text"]}""")
                    break
                else:
                    result = json.loads(recognizer.PartialResult())
                    logger.debug(f"""[*] Partial: {result["partial"]}""")

            audio_stream.stop_stream()
            audio_stream.close()
            stream.terminate()
            result: str = result["text"]
            logger.debug(f"[*] Admin: {result}")
            return result
