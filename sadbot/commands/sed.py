"""Sed bot command"""

import re

from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class SedBotCommand(CommandInterface):
    """This is the sed bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching sed command"""
        return r"s/.*/.*[/g]*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
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
        reply_message = self.message_repository.get_previous_message(message, old)
        if reply_message is None:
            return None
        max_replace = 1
        if replace_all:
            max_replace = len(reply_message.text)
        if reply_message is not None:
            try:
                reply = re.sub(old, new, reply_message.text, max_replace)
                reply = "<" + reply_message.sender_name + ">: " + reply
                return BotReply(BOT_REPLY_TYPE_TEXT, reply_text=reply)
            except re.error:
                return None
        return None
