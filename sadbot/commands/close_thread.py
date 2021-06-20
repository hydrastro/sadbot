"""Close thread bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class CloseThreadBotCommand(CommandInterface):
    """This is the thread-closing bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the closure of a discussion"""
        return r"(\s)?(/[Tt][Hh][Rr][Ee][Aa][Dd]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Closes a discussion"""
        closed_thread_replies = [
            "rekt",
            "*This thread has been archived at RebeccaBlackTech*",
        ]
        return BotReply(
            BOT_REPLY_TYPE_TEXT, reply_text=random.choice(closed_thread_replies)
        )
