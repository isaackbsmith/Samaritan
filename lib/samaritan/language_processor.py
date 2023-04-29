import os
import json
import logging
import numpy as np
from lib.shared.utils import generate_response
from lib.shared.producer import producer
from lib.samaritan.intent_recognizer import IntentRecognizer
from lib.samaritan.memory import Memory
from lib.samaritan.message_handler import MessageHandler


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class LanguageProcessor:

    def __init__(self, base_dir) -> None:
        self.base_dir = base_dir
        self.db_path = self.base_dir.joinpath('data/memory.db')
        self.intents_path = self.base_dir.joinpath('intel/skills/intents.json')
        self.threshold = 0.75
        self.memory = Memory(self.base_dir)
        self.conversation = MessageHandler(self.base_dir, producer)
        self.intent_recognizer = IntentRecognizer(self.base_dir)

        if not os.path.isfile(self.db_path):
            self.memory.populate_db()

        with open(self.intents_path) as intents:
            self.intents = json.load(intents)

    def execute(self, content: str, reply_to: str, body: bytes):
        action: str
        data: dict

        # Perform actions based on the type of content
        if content == "application/json":
            logger.debug('[*] Message received. Decoding...')
            try:
                data = json.loads(body.decode("utf-8"))
                action = data["action"]
            except:
                logger.error(
                    '[*] Could not load response as JSON or extract key of "type"')
        elif content == "audio/wav":
            logger.info('[*] A placeholder for an audio processor')

        logger.debug(f'[*] Peforming action: {action}')

        if action == "getResponse":
            result: dict
            text: str = data["text"]
            logger.debug(f'[*] Running prediction for: {text}')
            prob, group = self.intent_recognizer.evaluate(text)

            logger.debug(
                f"[*] Intent Classifier found {str(prob.item())} percent match to {str(group)}")

            if prob.item() > self.threshold:
                for intent in self.intents["intents"]:
                    if group == intent["group"]:
                        if len(intent["context"]) > 0:
                            result = self.conversation.get_reply(
                                intent["context"])
                        else:
                            response: str = np.random.choice(
                                intent["responses"])
                            result = generate_response(response, "", "")
            else:
                response = "Sorry, I'm having trouble understanding you"
                result = generate_response(response, "", "")

            payload = {
                "mode": "conversation",
                "result": result
            }
            body = json.dumps(payload)
            print(body)
            logger.debug(f"[*] Sending intent result to {reply_to}")
            result = self.conversation.send_message(reply_to, body)
        else:
            logger.warning(
                f'[*] The action {action} has no code to handle it.')
