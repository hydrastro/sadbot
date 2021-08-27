"""Channel bot command"""

import re
import html
from typing import Optional, List
import requests
import html2text

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class ChannelBotCommand(CommandInterface):
    """This is the channel bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching 4channel commands"""
        return r".*https://boards.4chan(nel)?.org/.*?/thread/[0-9]*?.*"

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
                r"https://boards.4chan(?:nel)?.org/.*?/thread/[0-9]*", message.text
            )
            req_url = url[0]
            req = requests.get(req_url)
            post = re.findall(
                r'post op".*?fileThu.*?href=\"[/][/](.*?)\".*?bloc.*?>(.*?)<[/]blo',
                req.text,
            )
            if not post:
                return None
            post = post[0]
            image = post[0]
            text = html.unescape(post[1])
            text = html2text.html2text(text)
            text = "Post: " + text + "\n" + "https://" + image + "\n"
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=text)]
        except (re.error, requests.ConnectionError):
            return None
