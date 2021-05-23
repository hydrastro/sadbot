"""Amogus bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class AmogusBotCommand(CommandsInterface):
    """This is the amogus bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r".*([Aa][Mm][Oo][Gg][Uu][Ss]).*|([Ss][Uu][Ss])"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Amogus"""
        amogus_replies = [
            "amogus",
            "sus",
            f"i saw the sus impostor {message.sender_name} vent in elec",
        ]
        return random.choice(amogus_replies)
