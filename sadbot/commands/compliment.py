"""Compliment bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class ComplimentBotCommand(CommandInterface):
    """This is the compliment bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching compliments"""
        return r".*(([Gg][Oo]{2}[Dd]|[Bb][Aa][Ss][Ee][Dd]|[Nn][Ii][Cc][Ee])(\s+[Bb][Oo][Tt])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
        """Gets a reply for when the bot receives a compliment"""
        compliment_replies = [
            "t-thwanks s-senpaii *starts twerking*",
            "at your service, sir",
            "thank youu!!",
            "good human",
        ]
        return [
            BotReply(BOT_REPLY_TYPE_TEXT, reply_text=random.choice(compliment_replies))
        ]
