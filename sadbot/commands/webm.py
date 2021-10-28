"""Webm bot command"""
from typing import Optional, List
import random
import subprocess
import os

from sadbot.command_interface import BOT_HANDLER_TYPE_DOCUMENT, CommandInterface
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_VIDEO

from sadbot.message import Message
from sadbot.app import App


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
        mime_type = "video/webm"
        if message.mime_type != mime_type:
            return None
        file_bytes = self.app.get_file_from_id(message.file_id)
        if file_bytes is None:
            return None
        name = str(random.randint(0, 10000000000))
        with open(name, "wb") as file:
            file.write(file_bytes)
        output = name + ".mp4"
        retcode = subprocess.call(
            ["ffmpeg", "-i", name, "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", output],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if retcode != 0:
            return None
        with open(output, "rb") as file:
            output_bytes = file.read()
        os.remove(name)
        os.remove(output)
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=output_bytes,
            ),
        ]
