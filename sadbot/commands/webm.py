"""Webm bot command"""
import os
import random
import subprocess
from typing import List, Optional

from sadbot.app import App
from sadbot.bot_action import BOT_ACTION_TYPE_REPLY_VIDEO, BotAction
from sadbot.command_interface import BOT_HANDLER_TYPE_DOCUMENT, CommandInterface
from sadbot.functions import webm_to_mp4_convert
from sadbot.message import Message


class WebmBotCommand(CommandInterface):
    """This is the sample command bot command class"""

    def __init__(
        self,
        app: App,
    ):
        """Initializes the webm command"""
        self.app = app

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_DOCUMENT

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""
        return "sus"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the command output"""
        if message is None:
            return None
        if message.mime_type is None:
            return None
        mime_types = ["video/webm", "video/x-matroska"]
        if message.mime_type not in mime_types:
            return None
        file_bytes = self.app.get_file_from_id(message.file_id)
        if file_bytes is None:
            return None
        mp4 = webm_to_mp4_convert(file_bytes)
        if not mp4:
            return None
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=mp4,
            ),
        ]
