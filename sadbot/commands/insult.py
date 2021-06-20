"""Insult bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class InsultBotCommand(CommandInterface):
    """This is the insult bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching insults"""
        return r".*(([Bb][Aa][Dd]|[Ss][Tt][Uu][Pp][Ii][Dd]|[Ss][Hh][Ii][Tt])(\s+[Bb][Oo][Tt])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
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
        return BotReply(BOT_REPLY_TYPE_TEXT, reply_text=random.choice(insult_replies))
