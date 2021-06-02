"""Roll bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class RollBotCommand(CommandsInterface):
    """This is the roll bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roll command"""
        return r"(\.[Rr][Oo][Ll]{2}).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Rolls a number"""
        return str(random.randint(0, 9))
