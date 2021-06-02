"""Ping bot command"""

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class PingBotCommand(CommandsInterface):
    """This is the ping bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Pp][Ii][Nn][Gg])).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns pong"""
        return "pong"
