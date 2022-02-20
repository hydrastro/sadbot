"""Compliment bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class ComplimentBotCommand(CommandInterface):
    """This is the compliment bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching compliments"""
        return r""".*(([Gg][Oo]{2}[Dd]|[Bb][Aa][Ss][Ee][Dd]|[Nn][Ii][Cc][Ee]|[Tt][Hh][Aa][Nn][Kk])
        (\s+[Bb][Oo][Tt])).*"""

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Gets a reply for when the bot receives a compliment"""
        compliment_replies = [
            "t-thwanks s-senpaii *starts twerking*",
            "at your service, sir",
            "thank youu!!",
            "good human",
        ]
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text=random.choice(compliment_replies)
            )
        ]
