"""Schizo bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class SchizoBotCommand(CommandInterface):
    """This is the schizo bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the schizo command"""
        return r".*([Gg][Oo]\s+[Ss][Cc][Hh][Ii][Zz][Oo]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Goes schizo"""
        return BotReply(
            BOT_REPLY_TYPE_TEXT,
            reply_text=str(random.randint(0, 999999999999999999999999999999999)),
        )
