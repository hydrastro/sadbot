"""Channel bot command"""

import re
import html
from typing import Optional, List
import requests
import markdownify

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class ChannelBotCommand(CommandInterface):
    """This is the channel bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching 4channel commands"""
        return r".*https://boards.4chan(nel)?.org/.*?/thread/[0-9]*?.*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return "MarkdownV2"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
        """Retrieve the description of a 4channel thread"""
        try:
            url = re.findall(
                r"https://boards.4chan(?:nel)?.org/.*?/thread/[0-9]*", message.text
            )
            url = url[0]
            req = requests.get(url)
            post = re.findall(
                r'post op".*?fileThu.*?href=\"[/][/](.*?)\".*?bloc.*?>(.*?)<[/]blo',
                req.text,
            )
            if not post:
                return None
            post = post[0]
            image = post[0]
            text = html.unescape(post[1])
            text = markdownify.markdownify(text)
            text = "Post: " + text + "\n" + "https://" + image + "\n"
            return [BotReply(BOT_REPLY_TYPE_TEXT, reply_text=text)]
        except (re.error, requests.ConnectionError):
            return None
