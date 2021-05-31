"""Channel bot command"""

import re
import html
from typing import Optional

import requests
import markdownify

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class ChannelBotCommand(CommandsInterface):
    """This is the channel bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching 4channel commands"""
        return r".*https://boards.4channel.org/.*?/thread/[0-9]*?.*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return "MarkdownV2"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Retrieve the description of a 4channel thread"""
        try:
            url = re.findall(r"https://boards.4channel.org/.*?/thread/[0-9]*", message.text)[0]
            req = requests.get(url)
            post = re.findall(r'post op".*?fileThu.*?img src=\"[/][/](.*?)\" alt.*?bloc.*?>(.*?)<[/]blo', req.text)[0]
            text = html.unescape(post[1])
            text = markdownify.markdownify(text)
            return text + "\n" + "https://" + post[0] + "\n"
        except:
            return None
