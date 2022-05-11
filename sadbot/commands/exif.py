"""EXIF bot command"""

from typing import Optional, List
import io
from exif import Image

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message, MESSAGE_FILE_TYPE_PHOTO, MESSAGE_FILE_TYPE_DOCUMENT
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.app import App


class ExifBotCommand(CommandInterface):
    """This is the exif bot command class"""

    def __init__(self, app: App, message_repository: MessageRepository):
        self.app = app
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching EXIF command"""
        return r"((!|\.)([Ee][Xx][Ii][Ff])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Performs the EXIF command on a given message"""
        if message is None or message.text is None:
            return None
        if message.reply_id is None:
            return None
        reply_message = self.message_repository.get_message_from_id(
            message.reply_id, message.chat_id
        )
        if reply_message is None:
            return None
        photo = self.get_photo_from_message(reply_message)
        if photo is None:
            return [
                BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text="No photo specified.")
            ]
        image = Image(io.BytesIO(photo))
        if not image.has_exif:
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Image has no exif data."
                )
            ]
        reply_text = "```"
        for attr in image.list_all():
            try:
                value = getattr(image, attr)
            except (NotImplementedError, AttributeError) as _e:
                continue
            reply_text += f"({attr}) = {value}\n"
        reply_text += "```"
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_text_parse_mode="Markdown",
            )
        ]

    def get_photo_from_message(self, message: Message) -> Optional[bytes]:
        """Returns the image to process"""
        if message.file_type not in [
            MESSAGE_FILE_TYPE_PHOTO,
            MESSAGE_FILE_TYPE_DOCUMENT,
        ]:
            return None
        if message.file_type == MESSAGE_FILE_TYPE_DOCUMENT:
            if message.mime_type not in ["image/jpeg", "image/png"]:  # and so on..
                return None
        if message.file_id is None:
            return None
        photo = self.app.get_file_from_id(message.file_id)
        if photo is None:
            return None
        return photo
