"""Amogus bot command"""

import random
from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class AmogusBotCommand(CommandInterface):
    """This is the amogus bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r".*([Aa][Mm][Oo][Gg][Uu][Ss]).*|([Ss][Uu][Ss])"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Amogus"""
        amogus_replies = [
            "amogus",
            "sus",
            f"i saw the sus impostor {message.sender_name} vent in elec",
        ]
        return BotReply(BOT_REPLY_TYPE_TEXT, reply_text=random.choice(amogus_replies))
