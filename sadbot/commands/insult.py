"""Insult bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class InsultBotCommand(CommandInterface):
    """This is the insult bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching insults"""
        return r".*(([Bb][Aa][Dd]|[Ss][Tt][Uu][Pp][Ii][Dd]|[Ss][Hh][Ii][Tt])(\s+[Bb][Oo][Tt])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Gets a reply for when the bot receives an insult"""
        insult_replies = [
            "no u",
            "take that back",
            "contribute to make me better: http://github.com/hydrastro/sadbot",
            "stupid human",
            "sTuPiD bOt1!1",
            "lord, have mercy: they don't know that they're saying.",
            "seethe dilate cope freetards btfo",
        ]
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text=random.choice(insult_replies)
            )
        ]
