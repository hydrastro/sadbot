"""Letsdo bot command"""

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class LetsdoBotCommand(CommandsInterface):
    """This is the letsdo bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching letsdo commands"""
        return r"((!|\.)([Ll][Ee][Tt][Ss][Dd][Oo]\s+\w+))"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns letsdo"""
        this = message.text[8:]
        return f"let's do {this}! {this} {this} toe {this} banana fanna foe f{this[1:]} me my moe m{this[1:]}, {this}"
