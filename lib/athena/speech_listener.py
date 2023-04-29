import json
import time
import signal
import logging
from lib.shared.producer import producer
from lib.athena.conversation_handler import ConversationHandler
from lib.athena.wakeword_detector import WakewordDetector


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class SpeechListener:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.interrupted = False
        self.conversation = ConversationHandler(self.config)
        self.wakeword_detector = WakewordDetector(self.config)
        self.config["AVG_NOISE"] = 100

    def signal_handler(self, signal, frame):
        logger.debug("[*] Wake word signal handler called")
        self.interrupted = True
        quit()

    def interrupt_callback(self):
        if not self.config["LISTEN"]:
            self.interrupted = True
        return self.interrupted

    def wait_until_listen(self):
        logger.debug("[*] Monitoring the LISTEN variable")
        self.interrupted = False
        while True:
            if self.config["LISTEN"]:
                self.passive_listen()
            time.sleep(1)

    def passive_listen(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.wakeword_detector
        logger.debug("[*] System is passively listening")
        self.wakeword_detector.detect(
            detected_callbackk=self.active_listen,
            interrupt_check=self.interrupt_callback,
            sleep_time=0.03
        )
        self.wakeword_detector.terminate()
        self.wait_until_listen()

    def active_listen(self):
        if not self.config["LISTEN"]:
            logger.debug("[*] Wakeword detected, system is busy")
        else:
            self.config["LISTEN"] = False
            logger.debug("[*] Wakeword detected, actively listening")
            response = self.conversation.listen()
            payload = {
                "action": "getResponse",
                "text": response
            }
            body = json.dumps(payload)
            producer.produce("Samaritan", "athena::GetReply",
                             self.config["NAME"], body)
            self.config["LISTEN"] = True
        self.wait_until_listen()


def listen(config: dict):
    speech_listener = SpeechListener(config)
    speech_listener.passive_listen()
