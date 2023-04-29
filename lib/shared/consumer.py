import pika
import yaml
import logging
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

CONFIG_DIR = '/archive/WorkStation/Aletheia/samaritan/settings.yaml'
with open(CONFIG_DIR) as f:
    config = yaml.safe_load(f)


class Consumer:

    def __init__(self, server: int, port: int, username: str, password: str) -> None:
        self.host = "/"
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def _init_channel(self) -> BlockingChannel:
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                self.server, self.port, self.host, credentials)
            connection = pika.BlockingConnection(parameters)
            logger.debug(f"[*] Connected to the exchange at {self.server}")
            return connection.channel()
        except pika.exceptions.ConnectionClosed:
            logger.error(
                f"[*] Unable to connect to the exchange at {self.server}")

    def consume(self, queue: str, callback) -> None:
        try:
            logger.debug(f"[*] Listening on {queue}'s channel")
            channel = self._init_channel()
            channel.queue_declare(queue)
            channel.basic_consume(
                queue=queue, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except pika.exceptions.ConnectionClosed:
            logger.error(f"[*] Failed to listen on {queue}'s channel.")


consumer = Consumer(config["QUEUE"]["SERVER"], config["QUEUE"]
                    ["PORT"], config["QUEUE"]["USERNAME"], config["QUEUE"]["PASSWORD"])
