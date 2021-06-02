"""Leaf bot command"""

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class CanadianBotCommand(CommandsInterface):
    """This is the leaf bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"((!|\.)([Ll][Ee][Aa][Ff]|[Cc][Aa][Nn][Aa][Dd][Ii][Aa][Nn])).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns leaf"""
        return "🇨🇦"
