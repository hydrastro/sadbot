"""Schizo bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class SchizoBotCommand(CommandInterface):
    """This is the schizo bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the schizo command"""
        return r".*([Gg][Oo](\s+)?[Ss][Cc][Hh][Ii][Zz][Oo]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Goes schizo"""
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=str(random.randint(0, 999999999999999999999999999999999)),
            )
        ]
