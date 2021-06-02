""" This module contains the main app class and friends """

import glob
import json
import re
import sqlite3
import time
from os.path import dirname, basename, isfile, join
from typing import Optional, Dict

import requests

from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.commands import *
from sadbot.config import MAX_REPLY_LENGTH, UPDATES_TIMEOUT


def snake_to_pascal_case(snake_str: str):
    """Converts a given snake_case string to PascalCase"""
    components = snake_str.split("_")
    return "".join(x.title() for x in components[0:])


class App:
    """Main app class, starts the bot when it's called"""

    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.classes = {}
        con = sqlite3.connect("./messages.db")
        print(con)
        self.classes.update({"Connection": con})
        self.message_repository = MessageRepository(con)
        self.classes.update({"MessageRepository": self.message_repository})
        self.commands = []
        self.load_commands()
        self.start_bot()

    def load_commands(self):
        """Loads the bot commands"""
        commands = glob.glob(join(dirname(__file__), "commands", "*.py"))
        for command_name in [basename(f)[:-3] for f in commands if isfile(f)]:
            if command_name in ("__init__", "interface"):
                continue
            class_name = snake_to_pascal_case(command_name) + "BotCommand"
            arguments = {}
            command_class = getattr(globals()[command_name], class_name)
            print(f"{class_name} class dependencies: ")
            if command_class.__init__.__class__.__name__ == "function":
                arguments_list = command_class.__init__.__annotations__
                for argument_name in arguments_list:
                    print(self.classes[arguments_list[argument_name].__name__])
                    arguments.update(
                        {
                            argument_name: self.classes[
                                arguments_list[argument_name].__name__
                            ]
                        }
                    )
            print("\n")
            command_class = command_class(*arguments)
            self.commands.append(
                {"regex": command_class.command_regex, "class": command_class}
            )

    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict]:
        """Retrieves updates from the telelegram API"""
        url = f"{self.base_url}getUpdates?timeout={UPDATES_TIMEOUT}"
        if offset:
            url = f"{url}&offset={offset + 1}"
        req = requests.get(url)
        if not req.ok:
            print(f"Failed to retrieve updates from server - details: {req.json()}")
            return None

        return json.loads(req.content)

    def send_message(
        self, message: Message, parsemode: Optional[str]
    ) -> Optional[Dict]:
        """Sends message to some chat using api"""
        if not message:
            return None
        if len(message.text) > MAX_REPLY_LENGTH:
            message.text = message.text[:80] + "..."

        data = {"chat_id": message.chat_id, "text": message.text}
        if parsemode is not None:
            data.update({"parsemode": parsemode})
        req = requests.post(
            f"{self.base_url}sendMessage",
            data=data,
            headers={"Conent-Type": "application/json"},
        )

        if not req.ok:
            print(f"Failed sending message - details: {req.json()}")
            return None

        return json.loads(req.content)

    def get_replies(self, message: Message) -> Optional[dict]:
        """Checks if a bot command is triggered and gets its reply"""
        text = message.text
        if not text:
            return None
        messages = []
        for command in self.commands:
            try:
                if re.fullmatch(re.compile(command["regex"]), text):
                    reply_message = command["class"].get_reply(message)
                    if reply_message is None:
                        continue
                    messages.append(
                        {
                            "message": reply_message,
                            "parsemode": command["class"].parsemode,
                        }
                    )
            except re.error:
                return None
        return messages

    def start_bot(self) -> None:
        """Starts the bot"""
        update_id = None
        while True:
            updates = self.get_updates(offset=update_id) or {}
            for item in updates.get("result", []):
                update_id = item["update_id"]
                try:
                    text = str(item["message"]["text"])
                except (ValueError, KeyError, TypeError):
                    continue

                if not text:
                    continue

                message = item["message"]
                message = Message(
                    message["message_id"],
                    message["from"]["first_name"],
                    message["from"]["id"],
                    message["chat"]["id"],
                    text,
                    message.get("reply_to_message", {}).get("message_id"),
                )
                replies_info = self.get_replies(message)
                self.message_repository.insert_message(message)
                if replies_info is None:
                    continue
                for reply_info in replies_info:
                    reply = reply_info["message"]
                    new_message = Message(chat_id=message.chat_id, text=reply)
                    sent_message = (
                        self.send_message(new_message, reply_info["parsemode"]) or {}
                    )
                    time.sleep(1)
                    if sent_message.get("result"):
                        result = sent_message.get("result")
                        message = Message(
                            result["message_id"],
                            result["from"]["first_name"],
                            result["from"]["id"],
                            message.chat_id,
                            reply,
                            None,
                        )
                        self.message_repository.insert_message(message)
            time.sleep(1)
