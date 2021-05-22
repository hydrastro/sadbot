""" This module contains the main app class and friends """

import glob
import json
import re
import sqlite3
import time
import urllib.parse
from os.path import dirname, basename, isfile, join
from typing import Optional, Dict

import requests

from sadbot.message import Message
from sadbot.commands import *


def snake_to_pascal_case(snake_str: str):
    """Converts a given snake_case string to PascalCase"""
    components = snake_str.split("_")
    return "".join(x.title() for x in components[0:])


def _create_func(x_val, y_val) -> int:
    """Labda function for the regex query"""
    return 1 if re.search(x_val, y_val) else 0


class App:
    """Main app class. when called it starts the bot"""

    def __init__(self, token: str) -> None:
        self.con = sqlite3.connect("./messages.db")
        self.con.create_function("regexp", 2, _create_func)
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.con.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
              MessageID        integer,
              SenderName       text,
              SenderID         int,
              ChatID           integer,
              Message          text,
              ReplyToMessageID int
            )"""
        )
        self.commands = []
        self.load_commands()
        self.start_bot()

    def load_commands(self):
        """Loads the bot commands"""
        commands = glob.glob(join(dirname(__file__), "commands", "*.py"))
        for command_name in [basename(f)[:-3] for f in commands if isfile(f)]:
            if command_name in ("__init__", "interface"):
                continue
            command_class = getattr(
                globals()[command_name],
                snake_to_pascal_case(command_name) + "BotCommand",
            )(self.con)
            self.commands.append(
                {"regex": command_class.get_regex(), "class": command_class}
            )

    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict]:
        """Retrieves updates from the telelegram API"""
        url = f"{self.base_url}getUpdates?timeout=50"
        if offset:
            url = f"{url}&offset={offset + 1}"
        req = requests.get(url)
        if not req.ok:
            print(f"Failed to retrieve updates from server - details: {req.json()}")
            return None

        return json.loads(req.content)

    def send_message(self, message: Message) -> Optional[Dict]:
        """Sends message to some chat using api"""
        if not message:
            return None
        message.text = urllib.parse.quote(message.text)

        url = (
            f"{self.base_url}sendMessage?"
            f"chat_id={message.chat_id}&text={message.text}"
        )
        req = requests.get(url)
        if not req.ok:
            print(f"Failed sending message - details: {req.json()}")
            return None

        return json.loads(req.content)

    def get_reply(self, message: Message) -> Optional[str]:
        """Checks if a bot command is triggered and gets its reply"""
        text = message.text
        if not text:
            return None
        text = text.lower()
        for command in self.commands:
            try:
                # TODO: allow partial match
                if re.fullmatch(re.compile(command["regex"]), text):
                    return command["class"].get_reply(message)
            except re.error:
                return None
        return None

    def insert_message(self, message: Message) -> None:
        """Inserts a message into the database"""
        query = """
          INSERT INTO messages (
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID
          ) VALUES (?, ?, ?, ?, ?, ?)
        """
        self.con.execute(
            query,
            (
                message.id,
                message.sender_name,
                message.sender_id,
                message.chat_id,
                message.text,
                message.reply_id,
            ),
        )
        self.con.commit()

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
                reply = self.get_reply(message)
                self.insert_message(message)
                if not reply:
                    continue

                new_message = Message(chat_id=message.chat_id, text=reply)
                sent_message = self.send_message(new_message) or {}
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
                    self.insert_message(message)
            time.sleep(1)
