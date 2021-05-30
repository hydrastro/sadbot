"""Channel bot command"""

import re
import html

from typing import Optional

import markdownify
import requests
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
            thread_post = re.findall(
                r"https://boards.4channel.org/.*?/thread/[0-9]*", message.text
            )
            req = requests.get(thread_post[0])
            posts_list = re.findall(
                (
                    r'post op".*?fileThumb.*?img src=\"[/][/](.*?)\" alt.'
                    r"*?blockquote .*?>(.*?)<[/]blockquote"
                ),
                req.text,
            )
            text = html.unescape(posts_list[0][1])
            text = markdownify.markdownify(text)
            return text + "\n" + "https://" + posts_list[0][0] + "\n"
        except (re.error, requests.ConnectionError):
            return None
