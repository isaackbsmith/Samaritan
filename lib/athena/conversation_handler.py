import re
import json
import time
import datetime
import logging
from lib.athena.speech_synthesizer import SpeechSynthesizer
from lib.athena.speech_recognizer import SpeechRecognizer
from lib.shared.producer import producer

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class ConversationHandler:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.stt = SpeechSynthesizer()
        self.speech_processor = SpeechRecognizer()

    def listen(self):
        self.config["LISTEN"] = False
        result = self.speech_processor.listen()
        logger.debug("[*] Finished listening to Admin")
        self.config["LISTEN"] = True
        return result

    def clean_response(self, response: str):
        if '#DAY#' in response:
            now = datetime.datetime.now()
            hour = now.hour
            if hour < 12:
                day = "Morning"
            elif hour < 18:
                day = "Afternoon"
            else:
                day = "Evening"
            response = response.replace('#DAY#', day)

        if '#TIME#' in response:
            now = datetime.datetime.now()
            time = datetime.datetime.now().strftime("%I:%M")
            hour = now.hour
            if hour < 12:
                day = "A M"
            elif hour < 18:
                day = "P M"
            else:
                day = "P M"
            curr_time = f"The current time is {time} {day}"
            response = response.replace('#TIME#', curr_time)

        if '#NAME#' in response:
            try:
                name = self.CONFIG["RECOGNIZED"]
            except:
                name = ""
            response = response.replace('#NAME#', name)

        # Correct representation of a year
        year_regex = re.compile(r'(\b)(\d\d)([1-9]\d)(\b)')
        response = year_regex.sub('\g<1>\g<2> \g<3>\g<4>', response)

        return response

    def listen_for_reply(self, app_id: str = "GetReply"):
        if not self.config["LISTEN"]:
            logger.debug("[*] system is busy")
        else:
            self.config["LISTEN"] = False
            logger.debug("[*] listening for reply")
            response = self.listen()
            payload = {
                "action": "getResponse",
                "text": response
            }
            body = json.dumps(payload)
            producer.produce(
                "Samaritan", f"athena::{app_id}", self.config["NAME"], body)
            self.config["LISTEN"] = True

    # Check for a Yes or No. Allows for one loop if no answer.
    # TODO use sentiment analysis later on to determine positive or negative response
    def get_yes_or_no(self, question):
        logger.debug("[*] Running get_yes_or_no function")

        # Listen for a response from the speaker
        response = self.listen()

        # first check for yes or no
        if bool(re.search(r'\bYES\b', response, re.IGNORECASE)):
            return "YES"
        elif bool(re.search(r'\bNO\b', response, re.IGNORECASE)):
            return "NO"
        else:
            self.say(f"Sorry, I did not hear a yes or no. {question}")
            response = self.listen()

        # second check for yes or no
        if bool(re.search(r'\bYES\b', response, re.IGNORECASE)):
            return "YES"
        else:
            return "NO"

    def execute_reply(self, response: str, action: str):
        logger.debug(
            f"[*] Running execute_reply for function {action} and text {response}")

        # if the text is "wait(xx)" where xx is an integer then wait for that time (in seconds)
        if re.search(r'^wait\([0-9]+\)$', response) is not None:
            text = response.upper()
            text = text.replace('WAIT(', '').replace(')', '')
            num = int(text)
            time.sleep(num)
        else:
            result = self.clean_response(response)
            self.stt.say(result)

        # if there is a function mentioned run it and get the results
        if action:
            action = action.strip()
            if action == "yesNo":
                logger.debug(f"[*] Listening for a YES or a NO")
                self.listen_for_reply("getYesOrNo")
            elif action == "pauseListen":
                logger.debug(f"[*] Listening for an answer")
                self.listen_for_reply("getReply")
            else:
                logger.debug(f"[*] No handler for function {action}")
                result = f"Sorry, I dont know what to do about {action}"
                self.stt.say(result)

    def start_conversation(self, conversation: dict):
        if not conversation or len(conversation) == 0:
            self.stt.say("Sorry, I could not work out what to say.")
        else:
            self.execute_reply(
                conversation['response'], conversation['action'])
