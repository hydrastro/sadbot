"""Sed bot command"""

import re

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class SedBotCommand(CommandsInterface):
    """This is the sed bot command class"""

    def __init__(self, con: str):
        self.con = con

    def get_regex(self) -> str:
        """Returns the regex for matching sed command"""
        return r"s/.*/.*[/g]*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
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

    def get_previous_message(self, message: Message, reg: str) -> Optional[Message]:
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
        if data is not None:
            return Message(*data)
        return None
