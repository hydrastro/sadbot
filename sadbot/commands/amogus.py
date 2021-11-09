"""Amogus bot command"""

import random
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class AmogusBotCommand(CommandInterface):
    """This is the amogus bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"(.*([Aa][Mm][Oo][Gg][Uu][Ss]).*|\s([Ss][Uu][Ss])|[Ss][Uu][Ss])"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Amogus"""
        if message is None:
            return None
        # Handles bot names
        # Kinda shitty solution, but it `werks`
        if message.text is not None and "@" in message.text:
            return None
        reply_user = (
            message.sender_username
            if message.sender_username is not None
            else message.sender_name
        )
        amogus_replies = [
            "amogus",
            "sus",
            f"i saw the sus impostor {reply_user} vent in elec",
        ]
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text=random.choice(amogus_replies)
            )
        ]
