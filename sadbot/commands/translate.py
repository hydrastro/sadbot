"""Translate bot command"""

from typing import Optional, List
import re
import urllib.parse
import requests

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class TranslateBotCommand(CommandInterface):
    """This is the translate bot command class"""

    def __init__(self, message_repository: MessageRepository):
        """Initializes the transalte bot command class"""
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching translate commands"""
        return r"([.]|[!])[Tt]([Rr]|[Ll])(.*)"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Get the translation"""
        if message is None or message.text is None:
            return None
        try:
            reply_message = self.message_repository.get_reply_message(message)
            if reply_message is None or reply_message.text is None:
                return None
            lang = "en"
            if len(message.text) > 4:
                lang = message.text[4:]
            quote = urllib.parse.quote(reply_message.text)
            if quote is None:
                return None
            url = f"https://translate.google.com/m?q={quote}&tl={lang}"
            req = requests.get(url)
            result = re.findall(r"result-container\">(.*?)</", req.text)
            if not result:
                return None
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Translation: " + result[0]
                )
            ]
        except (re.error, requests.ConnectionError):
            return None
