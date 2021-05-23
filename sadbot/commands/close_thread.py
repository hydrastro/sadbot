"""Close thread bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class CloseThreadBotCommand(CommandsInterface):
    """This is the thread-closing bot command class"""

    def __init__(self, con: str):
        self.con = con

    @property
    def get_regex(self) -> str:
        """Returns the regex for matching the closure of a discussion"""
        return r"(/[Tt][Hh][Rr][Ee][Aa][Dd]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Closes a discussion"""
        closed_thread_replies = [
            "rekt",
            "*This thread has been archived at RebeccaBlackTech*",
        ]
        return random.choice(closed_thread_replies)
