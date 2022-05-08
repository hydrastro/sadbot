"""OCR bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message, MESSAGE_FILE_TYPE_PHOTO
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.app import App
from sadbot.classes.ocr import get_text


class OcrBotCommand(CommandInterface):
    """This is the ocr bot command class"""

    def __init__(self, app: App, message_repository: MessageRepository):
        self.app = app
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching OCR command"""
        return r"((!|\.)([Oo][Cc][Rr])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Performs the ocr command on a given message"""
        if message is None or message.text is None:
            return None
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
        lang = "eng"
        if len(split) > 1:
            lang = split[1]
        reply_text = "OCR:\n" + get_text(lang, photo)
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]

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
