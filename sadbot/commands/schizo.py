"""Schizo bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class SchizoBotCommand(CommandsInterface):
    """This is the schizo bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the schizo command"""
        return r".*([Gg][Oo]\s+[Ss][Cc][Hh][Ii][Zz][Oo]).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Goes schizo"""
        return str(random.randint(0, 999999999999999999999999999999999))
