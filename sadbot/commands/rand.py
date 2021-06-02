"""Rand bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.functions import safe_cast


class RandBotCommand(CommandsInterface):
    """This is the rand bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the rand command"""
        return r"[Rr][Aa][Nn][Dd]\([-]?[0-9]+,(\s+)?[-]?[0-9]+\).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Gets a random number in a user-defined range"""
        text = message.text[4:]
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
            text = text.replace(" ", "")
            min_rand, max_rand = text.split(",", 1)
            min_rand = safe_cast(min_rand, int, 0)
            max_rand = safe_cast(max_rand, int, 0)
            if min_rand <= max_rand:
                return str(random.randint(int(min_rand), int(max_rand)))
        return None
