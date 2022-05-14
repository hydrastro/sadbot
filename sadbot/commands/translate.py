"""Translate bot command"""
from typing import Optional, List
import re
import requests

from sadbot.commands import googletrans
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
            args = message.text.split(" ")
            dest = "en"
            src = "auto"
            if len(args) >= 2:
                dest = args[1]
            if len(args) >= 3:
                src = args[2]
            translator = googletrans.Translator()
            try:
                text = (
                    "Translation: "
                    + translator.translate(reply_message.text, dest=dest, src=src).text
                )
            except ValueError as error:
                text = str(error)
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text=text,
                    reply_to_message_id=reply_message.message_id,
                )
            ]

        except (re.error, requests.ConnectionError):
            return None
