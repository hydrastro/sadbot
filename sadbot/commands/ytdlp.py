"""YTDLP bot command"""

from typing import Optional, List

import random
import os

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_VIDEO


class YtdlpBotCommand(CommandInterface):
    """This is the YTDLP bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ytdlp commands"""
        return r"((!|\.)([Yy][Tt][Dd][Ll][Pp])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Tries to download a link provided by command"""
        if message is None or message.text is None:
            return []
        watch_url = message.text[7:]
        file_name = str(random.randint(10000000000, 35000000000))
        ret = os.system(f"yt-dlp -o {file_name} -f '(mp4)[filesize<25M]' {watch_url}")
        if ret != 0:
            BotAction(
                BOT_HANDLER_TYPE_MESSAGE,
                reply_text="Something went wrong",
            )
        with open(file_name, "rb") as file:
            buf = file.read()
        os.remove(file_name)
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=buf,
            )
        ]
