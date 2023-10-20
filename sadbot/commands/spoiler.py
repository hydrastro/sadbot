"""Spoiler bot command"""

import mimetypes
from typing import Optional, List
import markdown
import requests

from sadbot.app import App

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.config import MAX_REPLY_LENGTH_MEDIA, MAX_REPLY_LENGTH_TEXT
from sadbot.functions import webm_to_mp4_convert
from sadbot.message import (
    Message,
    MESSAGE_FILE_TYPE_PHOTO,
    MESSAGE_FILE_TYPE_VIDEO,
)
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import (
    BOT_ACTION_TYPE_NONE,
    BotAction,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_REPLY_VIDEO,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_REPLY_IMAGE,
)


class SpoilerBotCommand(CommandInterface):
    """This is the spoiler bot command class"""

    def __init__(self, app: App, message_repository: MessageRepository):
        """Initializes the spoiler command"""
        self.app = app
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching spoiler commands"""
        return r"(\.|!|/)([sS])(.*)"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Spoiler"""
        if message is None or message.text is None:
            return None
        splitted = message.text.split(" ")
        if len(splitted) > 1:
            link = splitted[1]
            req = requests.get(link)
            if link.endswith("webm"):
                output = webm_to_mp4_convert(req.content)
            else:
                output = req.content
            mimetype = mimetypes.guess_type(link, strict=False)
            if mimetype and mimetype[0] and mimetype[0].startswith("image"):
                action = BotAction(
                    BOT_ACTION_TYPE_REPLY_IMAGE, reply_image=output, reply_spoiler=True
                )
            elif mimetype and mimetype[0] and mimetype[0].startswith("video"):
                action = BotAction(
                    BOT_ACTION_TYPE_REPLY_VIDEO, reply_video=output, reply_spoiler=True
                )
            else:
                action = BotAction(BOT_ACTION_TYPE_NONE)
            return [
                BotAction(
                    BOT_ACTION_TYPE_DELETE_MESSAGE,
                    reply_delete_message_id=message.message_id,
                ),
                action,
            ]
        if message.reply_id is None:
            return None
        reply_message = self.message_repository.get_reply_message(message)
        if reply_message is None:
            return None
        if reply_message.text is None or reply_message.text.startswith("Sender: "):
            return None
        file_bytes = self.app.get_file_from_id(reply_message.file_id)
        sender = reply_message.sender_name
        if reply_message.sender_username:
            sender = f"@{reply_message.sender_username}"
        limit = MAX_REPLY_LENGTH_TEXT if file_bytes is None else MAX_REPLY_LENGTH_MEDIA
        if len(reply_message.text) > limit - 200:
            reply_text = reply_message.text[
                : reply_message.text[: limit - 200].rfind("\n")
            ]
        else:
            reply_text = reply_message.text
        reply_text = f"Sender: {sender}\n<span class='tg-spoiler'>{markdown.markdown(reply_text)}</span>"
        reply_text = reply_text.replace("<p>", "")
        reply_text = reply_text.replace("</p>", "")
        reply_text = reply_text.replace("<br />", "\n")
        reply_text = reply_text.replace("<blockquote>", "")
        reply_text = reply_text.replace("</blockquote>", "")
        if reply_message.file_type == MESSAGE_FILE_TYPE_PHOTO:
            action = BotAction(
                BOT_ACTION_TYPE_REPLY_IMAGE,
                reply_image=file_bytes,
                reply_spoiler=True,
                reply_text=reply_text,
                reply_text_parse_mode="HTML",
            )
        elif reply_message.file_type == MESSAGE_FILE_TYPE_VIDEO:
            action = BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=file_bytes,
                reply_spoiler=True,
                reply_text=reply_text,
                reply_text_parse_mode="HTML",
            )
        else:
            action = BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_text_parse_mode="HTML",
            )
        return [
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_delete_message_id=message.reply_id,
            ),
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_delete_message_id=message.message_id,
            ),
            action,
        ]
