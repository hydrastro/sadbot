"""Roulette bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class RouletteBotCommand(CommandsInterface):
    """This is the roulette bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roulette command"""
        return r"(\.[Rr][Oo][Uu][Ll][Ee][Tt]{2}[Ee]).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Plays the Russian roulette"""
        if random.randint(0, 5) == 0:
            return "OH SHIIii.. you're dead, lol."
        return "Eh.. you survived."
