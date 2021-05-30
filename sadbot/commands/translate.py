"""4channel bot command"""

import requests
import re
import html
import markdownify

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


class TranslateBotCommand(CommandsInterface):
    """This is the amogus bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching translate commands"""
        return r"([.]|[!])tr(.*)"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Get the translation"""
        try:
            m = self.message_repository.get_reply_message(message)
            lang = m.text[4:]
            url = f"https://translate.google.com/m?q={m.text}"
            req = requests.get(url)
            ans = re.findall(r"result-container\">(.*?)</", req.text)
            return ans[0]
        except:
            return ""