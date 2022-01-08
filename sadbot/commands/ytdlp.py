"""YTDLP bot command"""

from typing import Optional, List

import random
import os
from yt_dlp import YoutubeDL


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
        ydl_opts = {
            "format": "(mp4)[filesize<50M]",
            "outtmpl": file_name,
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([watch_url])
            # pylint: disable=bare-except
            except:
                return [
                    BotAction(
                        BOT_HANDLER_TYPE_MESSAGE,
                        reply_text="Something went wrong.",
                    )
                ]
        with open(file_name, "rb") as file:
            buf = file.read()
        os.remove(file_name)
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=buf,
            )
        ]
