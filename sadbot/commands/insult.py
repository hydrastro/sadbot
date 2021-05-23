"""Insult bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class InsultBotCommand(CommandsInterface):
    """This is the insult bot command class"""

    def __init__(self, con: str):
        self.con = con

    @property
    def get_regex(self) -> str:
        """Returns the regex for matching insults"""
        return r".*(([Bb][Aa][Dd]|[Ss][Tt][Uu][Pp][Ii][Dd])(\s+[Bb][Oo][Tt])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Gets a reply for when the bot receives an insult"""
        insult_replies = [
            "no u",
            "take that back",
            "contribute to make me better",
            "stupid human",
            "sTuPiD bOt1!1",
            "lord, have mercy: they don't know that they're saying.",
        ]
        return random.choice(insult_replies)
