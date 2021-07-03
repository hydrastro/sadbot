"""Translate bot command"""

from typing import Optional, List
import re
import requests

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class TranslateBotCommand(CommandInterface):
    """This is the translate bot command class"""

    def __init__(self, message_repository: MessageRepository):
        """Initializes the transalte bot command class"""
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching translate commands"""
        return r"([.]|[!])[Tt]([Rr]|[Ll])(.*)"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
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
            return [
                BotReply(BOT_REPLY_TYPE_TEXT, reply_text="Translation: " + result[0])
            ]
        except (re.error, requests.ConnectionError):
            return None
