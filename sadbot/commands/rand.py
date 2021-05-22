"""Rand bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class RandBotCommand(CommandsInterface):
    """This is the rand bot command class"""

    def __init__(self, con: str):
        self.con = con

    def get_regex(self) -> str:
        """Returns the regex for matching the rand command"""
        return r"^rand\([0-9]+,[0-9]+\)"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Gets a random number in a user-defined range"""
        text = message.text[4:]
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
            text.replace(" ", "")
            min_rand, max_rand = text.split(",", 1)
            if min_rand <= max_rand:
                return str(random.randint(int(min_rand), int(max_rand)))
        return None
