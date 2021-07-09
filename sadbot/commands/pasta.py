"""Pasta bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.config import PASTAS
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class PastaBotCommand(CommandInterface):
    """This is the pasta bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching pasta commands"""
        return r"((!|\.)([Pp][Aa][Ss][Tt][Aa])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns a pasta"""
        key = None
        if len(message.text) > 7:
            key = message.text[7:]
        if key is not None and key in PASTAS:
            reply = PASTAS[key]
        else:
            reply = random.choice(list(PASTAS.values()))
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply)]
