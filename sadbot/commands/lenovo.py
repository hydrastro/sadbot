"""Lenovo bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class LenovoBotCommand(CommandInterface):
    """This is the lenovo bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching lenovo commands"""
        return r".*[Ww][Hh](([Aa][Tt])|[Ii][Cc][Hh])([Ll][Aa][Pp][Tt][Oo][Pp]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
        """Returns lenovo"""
        based_models = [
            "X220",
            "X230" "T420",
            "W530" "T440",
            "W540",
            "T480",
            "X210",
            "X200",
            "X62",
            "X61",
            "T70",
        ]
        reply_text = "Lenovo Thinkpad " + random.choice(based_models)
        return [BotReply(BOT_REPLY_TYPE_TEXT, reply_text=reply_text)]
