"""Close thread bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_reply import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class CloseThreadBotCommand(CommandInterface):
    """This is the thread-closing bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the closure of a discussion"""
        return r"(\s)?(/[Tt][Hh][Rr][Ee][Aa][Dd]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Closes a discussion"""
        closed_thread_replies = [
            "rekt",
            "*This thread has been archived at RebeccaBlackTech*",
        ]
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=random.choice(closed_thread_replies),
            )
        ]
