"""Amogus bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_reply import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class AmogusBotCommand(CommandInterface):
    """This is the amogus bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r".*([Aa][Mm][Oo][Gg][Uu][Ss]).*|([Ss][Uu][Ss])"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Amogus"""
        amogus_replies = [
            "amogus",
            "sus",
            f"i saw the sus impostor {message.sender_name} vent in elec",
        ]
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=random.choice(amogus_replies))]
