"""Translate bot command"""

from typing import Optional
import re

import requests

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class TranslateBotCommand(CommandsInterface):
    """This is the translate bot command class"""

    def __init__(self, message_repository: MessageRepository):
        """Initializes the transalte bot command class"""
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching translate commands"""
        return r"([.]|[!])[Tt]([Rr]|[Ll])(.*)"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Get the translation"""
        try:
            reply_message = self.message_repository.get_reply_message(message)
            if reply_message is None:
                return None
            lang = "en"
            if len(message.text) > 4:
                lang = message.text[4:]
            url = f"https://translate.google.com/m?q={reply_message.text}&tl={lang}"
            req = requests.get(url)
            result = re.findall(r"result-container\">(.*?)</", req.text)
            if not result:
                return None
            return "Translation: " + result[0]
        except (re.error, requests.ConnectionError):
            return None
