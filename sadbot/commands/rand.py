"""Rand bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.functions import safe_cast
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class RandBotCommand(CommandInterface):
    """This is the rand bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the rand command"""
        return r"[Rr][Aa][Nn][Dd]\([-]?[0-9]+,(\s+)?[-]?[0-9]+\).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Gets a random number in a user-defined range"""
        text = message.text[4:]
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
            text = text.replace(" ", "")
            min_rand, max_rand = text.split(",", 1)
            min_rand = safe_cast(min_rand, int, 0)
            max_rand = safe_cast(max_rand, int, 0)
            if min_rand <= max_rand:
                return [
                    BotAction(
                        BOT_ACTION_TYPE_REPLY_TEXT,
                        reply_text=str(random.randint(int(min_rand), int(max_rand))),
                    )
                ]
        return None
