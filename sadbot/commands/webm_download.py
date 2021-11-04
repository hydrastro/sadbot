"""Webm Download bot command"""
import os
import random
import re
import subprocess
from typing import List, Optional, Pattern

import requests

from sadbot.bot_action import BOT_ACTION_TYPE_REPLY_VIDEO, BotAction
from sadbot.command_interface import BOT_HANDLER_TYPE_MESSAGE, CommandInterface
from sadbot.message import Entity, Message


def check_entity(message: Optional[Message], entity: Entity, reg: Pattern) -> bool:
    """Check if entitiy matches a pattern"""
    if message is None or message.text is None:
        return False
    text = message.text[entity.offset : entity.offset + entity.length]
    if reg.match(text):
        return True
    return False


class WebmDownloadBotCommand(CommandInterface):
    """This is the webm download command bot class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""
        return r"(.|\s)*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the command output"""
        if message is None or message.text is None or message.entities is None:
            return None
        text = message.text
        urls = map(
            lambda e: text[e.offset : e.offset + e.length],
            filter(
                lambda e: check_entity(
                    message, e, re.compile(".*?/[^/]*?[.](webm)|(mkv)")
                ),
                filter(lambda e: e.type == "url", message.entities),
            ),
        )
        actions: List[BotAction] = []
        for url in urls:
            try:
                resp = requests.get(url)
                if resp.status_code != 200:
                    continue
                file_name = f"{random.randint(213123, 3123123123213131)}.mp4"
                with open(file_name, "wb") as file:
                    file.write(resp.content)
            except requests.ConnectionError:
                continue
            output = file_name + ".mp4"
            retcode = subprocess.call(
                [
                    "ffmpeg",
                    "-i",
                    file_name,
                    "-vf",
                    "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    output,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if retcode != 0:
                return None
            with open(output, "rb") as file:
                byte_array = file.read()
            actions.append(
                BotAction(BOT_ACTION_TYPE_REPLY_VIDEO, reply_video=byte_array)
            )
            os.remove(file_name)
            os.remove(output)
        if len(actions) == 0:
            return None
        return actions
