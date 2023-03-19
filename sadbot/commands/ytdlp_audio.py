"""YTDLP Audio bot command"""

from typing import Optional, List

import random
import os
from io import BytesIO
from yt_dlp import YoutubeDL

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_AUDIO


class YtdlpAudioBotCommand(CommandInterface):
    """This is the YTDLP audio bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching yta commands"""
        return r"((!|\.)([Yy][Tt][Aa])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Tries to download a link provided by command"""
        if message is None or message.text is None:
            return []
        watch_url = message.text[5:]
        file_name = str(random.randint(10000000000, 35000000000))
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": file_name,
        }
        file_name = file_name + ".mp3"
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(watch_url)
                title = info_dict.get("title", None)
            # pylint: disable=bare-except
            except:
                return [
                    BotAction(
                        BOT_HANDLER_TYPE_MESSAGE,
                        reply_text="Something went wrong.",
                    )
                ]
        with open(file_name, "rb") as file:
            buf = BytesIO(file.read())
            buf.name = title
        os.remove(file_name)
        return [BotAction(BOT_ACTION_TYPE_REPLY_AUDIO, reply_audio=buf)]
