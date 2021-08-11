"""Cringe bot command"""

import logging
import random
import re
from typing import Optional, List
from dataclasses import dataclass
import requests

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.config import ECELEBS
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class CringeBotCommand(CommandInterface):
    """This is the schizo bot command class"""

    @property
    def handler_type(self) -> int:
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
        class EcelebClass:
            """Defines the dataclass for ecelebs"""

            url: str = ""
            regex: str = ""
            prefix: str = ""

        ecelebs = []
        for eceleb in ECELEBS:
            ecelebs.append(EcelebClass(**eceleb))
        lucky_eceleb = ecelebs[random.randint(0, len(ecelebs)) - 1]
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        }
        try:
            req = requests.get(
                lucky_eceleb.url, headers=headers, cookies={"CONSENT": "YES+42"}
            )
        except requests.exceptions.RequestException as exception:
            logging.error("An error occured while sending the eceleb request")
            logging.error(str(exception))
            return None
        if not req.ok:
            logging.warning("Failed to get eceleb data - details: %s", req.text)
            return None
        data = re.findall(re.compile(lucky_eceleb.regex), req.text)
        if data is None:
            logging.warning(
                "Failed to get eceleb data: regex gave no results - "
                "defails: eceleb: %s, regex: %s, data: %s",
                lucky_eceleb.prefix,
                lucky_eceleb.regex,
                req.text,
            )
            return None
        data = list(set(data))
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=f"{lucky_eceleb.prefix}{random.choice(data)}",
            )
        ]
