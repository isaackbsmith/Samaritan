import json
import logging
from lib.athena.conversation_handler import ConversationHandler


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class SpeechInterface:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.conversation = ConversationHandler(self.config)

    def execute(self, content: str, body: bytes):
        if content == "application/json":
            data: dict = json.loads(body.decode("utf-8"))
            logger.debug("[*] Finished loading json data")
            mode: str = data["mode"]

            if mode == "conversation":
                self.config["TALKING"] = True
                logger.info("[*] Admin is talking")
                conversation: dict = data["result"]
                self.conversation.start_conversation(conversation)
                self.config["TALKING"] = False
                logger.debug("[*] Admin is done talking")
            else:
                logger.debug(f"[*] No logic exists for {mode}")
        else:
            logger.debug(f"[*] No logic exists for {content}")
