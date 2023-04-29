import os
import yaml
import logging
from pathlib import Path
from lib.shared.consumer import consumer
from lib.samaritan.language_processor import LanguageProcessor


BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR.joinpath("settings.yaml")

# Load application configuration
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Setup logging
logging.basicConfig()
logger = logging.getLogger("SERVER")
if config["ROOT"]["DEBUG"]:
    logger.level = logging.DEBUG
else:
    logger.level = logging.INFO


# Initialize language processor
language_processor = LanguageProcessor(BASE_DIR)


def queue_callback(ch, method, properties, body) -> None:
    """Invoked whenever a message is recieved from a client"""
    app_id: str = properties.app_id
    content: str = properties.content_type
    reply_to: str = properties.reply_to

    logger.debug(
        f"[*] Message received from {reply_to}, App: {app_id}, content: {content}")

    if app_id == "athena::GetReply":
        language_processor.execute(content, reply_to, body)
    elif app_id == "athena::GetMessage":
        logger.debug("getMessage called. No logic exists")
    elif app_id == "athena::GetYesOrNo":
        logger.debug("getYesOrNo called. No logic exists")
    else:
        logger.error(
            f"[*] Message received from {reply_to} but no handler for {app_id}")


def main() -> None:
    logger.debug("[*] Loading models")
    consumer.consume(config["ROOT"]["NAME"], queue_callback)


if __name__ == "__main__":
    main()
