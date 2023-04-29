import json
import yaml
import logging
from pathlib import Path
from lib.shared.consumer import consumer
from multiprocessing import Process, Manager
from lib.athena.speech_listener import listen
from lib.athena.speech_interface import SpeechInterface

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR.joinpath("settings.yaml")

# Load application configuration
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Setup logging
logging.basicConfig()
logger = logging.getLogger(__name__)
if config["ROOT"]["DEBUG"]:
    logger.level = logging.DEBUG
else:
    logger.level = logging.INFO


def queue_callback(ch, method, properties, body):
    logger.debug("[*] Queue callback function triggered")
    app_id = properties.app_id
    content = properties.content_type
    reply_to = properties.reply_to
    logger.debug(
        f"[*] Message received from {reply_to} App: {app_id} content: {content}")

    if app_id == 'samaritan::GetMessage':
        speech_interface.execute(content, body)
    else:
        logger.error(
            f"[*] Message received from {reply_to} but no logic exists for {app_id}")


if __name__ == "__main__":
    # Setup CONFIG data to be shared with the modules
    mgr = Manager()
    config_mgr = mgr.dict()
    config_mgr["BASE_DIR"] = BASE_DIR
    config_mgr["LISTEN"] = True
    config_mgr["TALKING"] = False
    config_mgr["NAME"] = config['ENTITY']['NAME']

    # Start Listening to Admin
    logger.info("[*] Initializing system")
    speech_interface = SpeechInterface(config_mgr)
    try:
        # from client.libraries import voice_sensor
        speech_process = Process(target=listen, args=(config_mgr,))
        speech_process.start()
    except Exception as e:
        logger.error(f'[*] Failed to initialize speech interface: {e}')

    # Listen for incomming messages
    consumer.consume(config["ENTITY"]["NAME"], queue_callback)
