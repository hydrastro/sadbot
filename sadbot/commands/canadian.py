"""Leaf bot command"""

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class CanadianBotCommand(CommandsInterface):
    """This is the leaf bot command class"""

    def __init__(self, con: str):
        self.con = con

    def get_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"^((!|\.)(leaf|canadian))$"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns leaf"""
        return "🇨🇦"
