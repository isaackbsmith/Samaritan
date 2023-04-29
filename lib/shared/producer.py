import pika
import yaml
import logging


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

CONFIG_DIR = '/archive/WorkStation/Aletheia/samaritan/settings.yaml'
with open(CONFIG_DIR) as f:
    config = yaml.safe_load(f)


class Producer:

    def __init__(self, server: int, port: int, username: str, password: str) -> None:
        self.host = "/"
        self.credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(
            server, port, self.host, self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def produce(self, routing_key: str, app_id: str, reply_to: str, body: dict) -> None:
        try:
            self.channel.queue_declare(reply_to)
            properties = pika.BasicProperties(
                app_id=app_id, content_type="application/json", reply_to=reply_to)
            self.channel.basic_publish(
                exchange="", routing_key=routing_key, body=body, properties=properties)
            # self.connection.close()
        except Exception as e:
            print(e)
            logger.error(
                '[*] There was an error sending the message to the queue')


producer = Producer(config["QUEUE"]["SERVER"], config["QUEUE"]
                    ["PORT"], config["QUEUE"]["USERNAME"], config["QUEUE"]["PASSWORD"])
