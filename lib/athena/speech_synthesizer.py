import pyttsx3


class SpeechSynthesizer:

    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        # self.voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', self.voices[1].id)

    def say(self, phrase: str) -> None:
        self.engine.say(phrase)
        self.engine.runAndWait()
