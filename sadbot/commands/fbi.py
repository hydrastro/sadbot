"""FBI bot command"""

from typing import Optional

from sadbot.config import FBI_WORDS
from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class FbiBotCommand(CommandsInterface):
    """This is the FBI bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching 4channel commands"""
        return r".*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Return nothing. Just add to the database"""
        forbidden_words = []
        for word in FBI_WORDS:
            # the forbidden words should be case insensitive
            if word in message.text:
                forbidden_words.append(word)
        for word in forbidden_words:
            data = self.message_repository.get_fbi_entry(message, word)
            if data is None:
                self.message_repository.insert_fbi_entry(message, word)
                return None
            self.message_repository.update_fbi_entry(message, word)
        return None
