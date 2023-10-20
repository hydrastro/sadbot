"""Channel bot command"""

import re
import html
from typing import Optional, List
import requests
import html2text

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.functions import webm_to_mp4_convert
from sadbot.message import Message
from sadbot.bot_action import (
    BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
    BotAction,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_REPLY_PHOTO_ONLINE,
    BOT_ACTION_TYPE_REPLY_VIDEO,
)


class ChannelBotCommand(CommandInterface):
    """This is the channel bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching 4channel commands"""
        return r".*https://boards\.4chan(nel)?.org/.*?/thread/[0-9]*?.*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return "MarkdownV2"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Retrieve the description of a 4channel thread"""
        if message is None or message.text is None:
            return None
        try:
            url = re.findall(
                r"https://boards\.4chan(?:nel)?.org/.*?/thread/[0-9]*", message.text
            )
            req_url = url[0]
            req = requests.get(req_url)
            finds = re.findall(
                r'post op".*?fileThu.*?href=\"[/][/](.*?)\".*?bloc.*?>(.*?)<[/]blo',
                req.text,
            )
            if not finds:
                return None
            subject_finds = re.findall(r'<span class="subject">(.*?)</span>', req.text)
            find = finds[0]
            media = find[0]
            post = html2text.html2text(html.unescape(find[1]))
            if subject_finds and len(subject_finds[1]) > 0:
                subject = html2text.html2text(html.unescape(subject_finds[1]))
                text = f"Subject: {subject}\nPost: {post}\nLink: {req_url}\nMedia: https://{media}"
            else:
                text = f"Post: {post}\nLink: {req_url}\nMedia: https://{media}"

            action = None
            if media.endswith("webm"):
                file_bytes = requests.get(f"https://{media}").content
                output_bytes = webm_to_mp4_convert(file_bytes)
                action = BotAction(
                    BOT_ACTION_TYPE_REPLY_VIDEO,
                    reply_video=output_bytes,
                    reply_text=text,
                )
            elif media.endswith("gif"):
                action = BotAction(
                    BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
                    reply_online_media_url=f"https://{media}",
                    reply_text=text,
                )
            elif media.endswith("png") or media.endswith("jpg"):
                action = BotAction(
                    BOT_ACTION_TYPE_REPLY_PHOTO_ONLINE,
                    reply_text=text,
                    reply_online_photo_url=f"https://{media}",
                )
            else:
                action = BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text=text,
                )
            return [action]
        except (re.error, requests.ConnectionError):
            return None
