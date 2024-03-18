"""Translate bot command"""
from typing import Optional, List
import re
import requests

from sadbot.commands import googletrans
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT, BOT_ACTION_TYPE_REPLY_IMAGE
from sadbot.classes.ocr import get_text_and_translate
from sadbot.message import Message, MESSAGE_FILE_TYPE_PHOTO
from sadbot.app import App


class TranslateBotCommand(CommandInterface):
    """This is the translate bot command class"""

    def __init__(self, app: App, message_repository: MessageRepository):
        """Initializes the transalte bot command class"""
        self.app = app
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching translate commands"""
        return r"([.]|[!])[Tt]([Rr]|[Ll])(.*)"

    def get_photo_from_message(self, message: Message) -> Optional[bytes]:
        """Returns the image to process"""
        if message.file_type is not MESSAGE_FILE_TYPE_PHOTO:
            return None
        if message.file_id is None:
            return None
        photo = self.app.get_file_from_id(message.file_id)
        if photo is None:
            return None
        return photo

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Get the translation"""
        if message is None or message.text is None:
            return None
        try:
            reply_message = self.message_repository.get_reply_message(message)
            if reply_message is None or reply_message.text is None:
                """Performs the ocr command on a given message"""
                if message.reply_id is None:
                    photo = self.get_photo_from_message(message)
                else:
                    reply_message = self.message_repository.get_message_from_id(
                        message.reply_id, message.chat_id
                    )
                    if reply_message is None:
                        return None
                    photo = self.get_photo_from_message(reply_message)
                if photo is None:
                    return [
                        BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text="An error occured")
                    ]
                split = message.text.split()
                lang = "en"
                dest = "en"
                src = "auto"
                if len(split) > 1:
                    dest = split[1]
                if len(split) >= 2:
                    lang = split[2]
                if len(split) >= 3:
                    src = split[2]
                translator = googletrans.Translator()
                img = get_text_and_translate(lang, photo, translator, dest, src)
                return [BotAction(BOT_ACTION_TYPE_REPLY_IMAGE, reply_image=img)]
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
