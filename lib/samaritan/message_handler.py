import os
import json
import logging
from lib.shared.utils import SQLite, generate_response
from lib.shared.producer import Producer


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class MessageHandler:

    def __init__(self, base_dir: str, producer: Producer) -> None:
        self.base_dir = base_dir
        self._db_path = self.base_dir.joinpath('data/memory.db')
        self.producer = producer

    def compose_message(self, reply_to, response):
        result = {
            'mode': 'conversation',
            'response': response
        }
        body = json.dumps(result)
        result = self.send_message(reply_to, body)
        return body

    def send_message(self, reply_to, body):
        try:
            self.producer.produce(
                reply_to, "samaritan::GetMessage", "Athena", body)
        except Exception as e:
            logger.error(
                '[*] There was an error sending the message to the queue')
            print(e)
            return False
        return True

    def compose_query(self, table: str, category: str, item: str):
        sql = "SELECT response, action, next FROM " + \
            table + " WHERE Category = '" + category + "'"
        if str(item) != '0':
            sql += " AND item = " + str(item)
        else:
            sql += " ORDER BY RANDOM() LIMIT 1 ;"
        return sql

    def get_message_row(self, context: str):
        response: dict
        query_list: list
        row = context.split("-")
        category = row[1]
        item = row[2]
        sql = self.compose_query('Memories', category, item)

        with SQLite(self._db_path) as (connection, cursor):
            try:
                cursor.execute(sql)
                query_list = cursor.fetchall()
            except:
                connection.rollback()

            # insert result into the json data object
            if len(query_list) > 0:
                response = generate_response(
                    query_list[0][0], query_list[0][1], query_list[0][2])
            else:
                blob = 'Something went wrong. I could not find the requested chat entry'
                response = generate_response(blob, "", "")
            return response

    def get_reply(self, context='0-GREETA-0'):
        context_arr = context.split('-')

        if len(context_arr) == 2:
            context = f'0-{context}'

        logger.debug(f'[*] Creating conversation path with context: {context}')

        if "|" not in context and len(context) > 0:
            reply = self.get_message_row(context)
            return reply
