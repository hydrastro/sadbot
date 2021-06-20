"""Roll bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class RollBotCommand(CommandInterface):
    """This is the roll bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roll command"""
        return r"(\.[Rr][Oo][Ll]{2}).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Rolls a number"""
        return BotReply(BOT_REPLY_TYPE_TEXT, reply_text=str(random.randint(0, 9)))
