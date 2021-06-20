"""Rand bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.functions import safe_cast
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class RandBotCommand(CommandInterface):
    """This is the rand bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the rand command"""
        return r"[Rr][Aa][Nn][Dd]\([-]?[0-9]+,(\s+)?[-]?[0-9]+\).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Gets a random number in a user-defined range"""
        text = message.text[4:]
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
            text = text.replace(" ", "")
            min_rand, max_rand = text.split(",", 1)
            min_rand = safe_cast(min_rand, int, 0)
            max_rand = safe_cast(max_rand, int, 0)
            if min_rand <= max_rand:
                return BotReply(
                    BOT_REPLY_TYPE_TEXT,
                    reply_text=str(random.randint(int(min_rand), int(max_rand))),
                )
        return None
