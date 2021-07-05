"""Roll bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_reply import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class RollBotCommand(CommandInterface):
    """This is the roll bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roll command"""
        return r"(\.[Rr][Oo][Ll]{2}).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Rolls a number"""
        return [
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=str(random.randint(0, 9)))
        ]
