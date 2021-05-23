"""Rand bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class RandBotCommand(CommandsInterface):
    """This is the rand bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def get_regex(self) -> str:
        """Returns the regex for matching the rand command"""
        return r"[Rr][Aa][Nn][Dd]\([0-9]+,(\s+)?[0-9]+\).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Gets a random number in a user-defined range"""
        text = message.text[4:]
        print(text)
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
            text = text.replace(" ", "")
            min_rand, max_rand = text.split(",", 1)
            if min_rand <= max_rand:
                return str(random.randint(int(min_rand), int(max_rand)))
        return None
