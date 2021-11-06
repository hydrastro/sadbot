"""Spoiler bot command"""

from typing import Optional, List
import requests
from sadbot.app import App

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_REPLY_VIDEO,
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
        return r"(.|!)([sS][pP][oO][iI][lL][eE][rR])(.*)"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Spoiler"""
        if message is None or message.reply_id is None or message.text is None:
            return None
        reply_message = self.message_repository.get_reply_message(message)
        if reply_message is None or reply_message.file_id is None:
            return None
        file_bytes = self.app.get_file_from_id(reply_message.file_id)
        if file_bytes is None:
            return None
        files = {"file": file_bytes}
        try:
            req = requests.post("https://oshi.at", files=files)
            url = req.text.splitlines()[1].split(" ")[1]
        except (requests.ConnectionError, IndexError):
            return [
                BotAction(
                    BOT_ACTION_TYPE_DELETE_MESSAGE,
                    reply_delete_message_id=message.reply_id,
                ),
            ]

        if len(message.text) > 8:
            reason = message.text[8:]
        else:
            reason = "I don't care, kiddo."
        with open("sadbot/assets/cry_about_it.mp4", "rb") as file:
            video = file.read()
        return [
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_delete_message_id=message.reply_id,
            ),
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=video,
                reply_text=f"Download page: {url}\nReason: {reason}",
            ),
        ]
