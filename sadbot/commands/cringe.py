"""Cringe bot command"""

import random
import re
from typing import Optional, List
from dataclasses import dataclass
import requests

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.config import ECELEBS
from sadbot.bot_reply import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class CringeBotCommand(CommandInterface):
    """This is the schizo bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the cringe command"""
        return r"((!|\.)([Cc][Rr][Ii][Nn][Gg][Ee])).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return "HTML"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns cringy stuff"""

        @dataclass
        class Eceleb:
            """Defines the dataclass for ecelebs"""

            def __init__(self, url, regex, prefix):
                self.url = url
                self.regex = regex
                self.prefix = prefix

        ecelebs = []
        for eceleb in ECELEBS:
            ecelebs.append(
                Eceleb(
                    url=eceleb["url"], regex=eceleb["regex"], prefix=eceleb["prefix"]
                )
            )
        eceleb = ecelebs[random.randint(0, len(ecelebs)) - 1]
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        }
        req = requests.get(eceleb.url, headers=headers, cookies={"CONSENT": "YES+42"})
        if not req.ok:
            print(f"Failed to get eceleb data - details: {req.text}")
            return None
        data = re.findall(re.compile(eceleb.regex), req.text)
        if data is None:
            return None
        data = list(set(data))
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text=f"{eceleb.prefix}{random.choice(data)}"
            )
        ]
