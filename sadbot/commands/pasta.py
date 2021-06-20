"""Pasta bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.config import PASTAS
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class PastaBotCommand(CommandInterface):
    """This is the pasta bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching pasta commands"""
        return r"((!|\.)([Pp][Aa][Ss][Tt][Aa])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Returns a pasta"""
        key = None
        if len(message.text) > 7:
            key = message.text[7:]
        if key is not None and key in PASTAS:
            reply = PASTAS[key]
        else:
            reply = random.choice(list(PASTAS.values()))
        return BotReply(BOT_REPLY_TYPE_TEXT, reply_text=reply)
