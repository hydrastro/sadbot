""" This module contains the main app class and friends """

import json
import random
import re
import sqlite3
from typing import Optional, Dict

import requests

from sadbot.message import Message


def _create_func(x, y) -> int:  # pylint: disable=invalid-name
    return 1 if re.search(x, y) else 2


def random_insult() -> str:
    """Gets a reply for when the bot receives an insult"""
    insult_replies = [
        "no u",
        "take that back",
        "contribute to make me better",
        "stupid human",
        "sTuPiD bOt1!1",
        "lord, have mercy: they don't know that they're saying.",
    ]
    return random.choice(insult_replies)


def random_compliment() -> str:
    """Gets a reply for when the bot receives a compliment"""
    compliment_replies = [
        "t-thwanks s-senpaii *starts twerking*",
        "at your service, sir",
        "thank youu!!",
        "good human",
    ]
    return random.choice(compliment_replies)


def get_roulette() -> str:
    """Plays russian roulette"""
    if random.randint(0, 5) == 0:
        return "OH SHIIii.. you're dead, lol."
    return "Eh.. you survived."


def get_closed_thread() -> str:
    """Closes a discussion"""
    closed_thread_replies = [
        "rekt",
        "*This thread has been archived at RebeccaBlackTech*",
    ]
    return random.choice(closed_thread_replies)


def get_rand_command(message: Message) -> Optional[str]:
    """Returns a random number in a user-defined range"""
    text = message.text[4:]
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1]
        text.replace(" ", "")
        min_rand, max_rand = text.split(",", 1)
        if min_rand <= max_rand:
            return str(random.randint(int(min_rand), int(max_rand)))
    return None


def go_schizo() -> str:
    """Goes schizo"""
    return str(random.randint(0, 999999999999999999999999999999999))

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
        self.start_bot()

    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict]:
        """Retrieves updates from the telelegram API"""
        url = f"{self.base_url}getUpdates?timeout=50"
        if offset:
            url = f"{url}&offset={offset + 1}"
        req = requests.get(url)
        if not req.ok:
            print("Failed to retrieve updates from server")
            return None

        return json.loads(req.content)

    def send_message(self, message: Message) -> Optional[Dict]:
        """Sends message to some chat using api"""
        if not message:
            return None

        url = (
            f"{self.base_url}sendMessage?"
            f"chat_id={message.chat_id}&text={message.text}"
        )
        req = requests.get(url)
        if not req.ok:
            print("Failed sending message")
            return None

        return json.loads(req.content)

    def get_previous_message(self, message: Message, reg: str) -> Message:
        """Retrieves a previous message from the database matching a certain
        regex pattern
        """
        cur = self.con.cursor()
        query = """
          SELECT
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID
          FROM messages
          WHERE Message REGEXP ? AND ChatID = ?
        """
        params = [reg, message.chat_id]
        if message.reply_id:
            query += "AND MessageID = ? "
            params.append(message.reply_id)
        query += "ORDER BY MessageID DESC"
        cur.execute(query, params)
        data = cur.fetchone()
        return Message(*data)

    def get_sed_command(self, message: Message) -> Optional[str]:
        """Performs the sed command on a given message"""
        replace_all = False
        text = message.text
        if text.endswith("/"):
            text = text[:-1]
        if text.endswith("/g") and (text.count("/") > 2):
            replace_all = True
            text = text[:-2]
        first_split = text.split("/", 1)
        second_split = ["s"]
        second_split += first_split[1].rsplit("/", 1)
        if len(second_split) != 3:
            return None
        old = second_split[1]
        new = second_split[2]
        try:
            re.compile(old)
        except re.error:
            return None
        reply_message = self.get_previous_message(message, old)
        if reply_message is None:
            return None
        max_replace = 1
        if replace_all:
            max_replace = len(reply_message.text)
        if reply_message is not None:
            try:
                reply = re.sub(old, new, reply_message.text, max_replace)
                reply = "<" + reply_message.sender_name + ">: " + reply
                return reply
            except re.error:
                return None
        return None

    def get_reply(self, message: Message) -> Optional[str]:
        """Checks if a bot command is triggered and gets its reply"""
        text = message.text
        if not text:
            return None

        result: Optional[str] = None
        text = text.lower()
        if re.fullmatch(re.compile("s/.*/.*[/g]*"), text):
            result = self.get_sed_command(message)
        elif text.startswith(".roulette"):
            result = get_roulette()
        elif text == ".roll":
            result = str(random.randint(0, 10))
        elif text.startswith("rand"):
            result = get_rand_command(message)
        elif text in ("!leaf" or "!canadian"):
            result = "🇨🇦"
        elif text in ("/thread", "fpbp", "spbp"):
            result = get_closed_thread()
        elif text in ("stupid bot", "bad bot"):
            result = random_insult()
        elif text in ("good bot", "based bot"):
            result = random_compliment()
        elif text == "go schizo":
            result = go_schizo()

        return result

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
                except Exception:  # pylint: disable=broad-except
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
