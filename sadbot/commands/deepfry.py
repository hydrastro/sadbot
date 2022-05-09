"""Deepfry bot command"""

from typing import Optional, List, Tuple
import io


from PIL import Image, ImageOps, ImageEnhance
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message, MESSAGE_FILE_TYPE_PHOTO
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.app import App


class DeepfryBotCommand(CommandInterface):
    """This is the deepfry bot command class"""

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
        return r"((!|\.)([Dd][Ee][Ee][Pp][Ff][Rr][Yy])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Performs the deepfry command on a given message"""
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
        image = Image.open(io.BytesIO(photo))
        image = self.deepfry(image)
        return [BotAction(BOT_ACTION_TYPE_REPLY_IMAGE, reply_image=image)]

    @staticmethod
    def deepfry(
        img: Image,
        *,
        colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = (
            (254, 0, 2),
            (255, 255, 15),
        )
    ) -> Image:
        """Deepfries an image"""
        img = img.convert("RGB")
        width, height = img.width, img.height
        img = img.resize(
            (int(width**0.75), int(height**0.75)), resample=Image.LANCZOS
        )
        img = img.resize(
            (int(width**0.88), int(height**0.88)), resample=Image.BILINEAR
        )
        img = img.resize(
            (int(width**0.9), int(height**0.9)), resample=Image.BICUBIC
        )
        img = img.resize((width, height), resample=Image.BICUBIC)
        img = ImageOps.posterize(img, 4)

        r_idk = img.split()[0]
        r_idk = ImageEnhance.Contrast(r_idk).enhance(3.0)
        r_idk = ImageEnhance.Brightness(r_idk).enhance(1.5)
        r_idk = ImageOps.colorize(r_idk, colors[0], colors[1])

        img = Image.blend(img, r_idk, 0.75)
        img = ImageEnhance.Sharpness(img).enhance(100.0)
        img_byte = io.BytesIO()
        img.save(img_byte, format="png")
        img_byte = img_byte.getvalue()
        return img_byte

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
