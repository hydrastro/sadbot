"""Weed bot command"""

from typing import Optional, List
import random

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class WeedBotCommand(CommandInterface):
    """This is the weed bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching lenovo commands"""
        return r".*([Ww][Aa][Nn][Tt]|[Ll][Ii][Kk][Ee]).*([Ww][Ee]{2}[Dd]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Politely refuses weed while staying cool cause my brain already smooth"""
        replies = [
            "Thank you for the offer, but I'm good",
            "No, thank you, I'm fine",
            "No, thanks, my brain already smooth enough",
            """I shalt decline thine propitious offer of inhaling plantam cannabinacearum in my
            lungs quod I hitherto feel accomplished about the life of mine person.""",
        ]
        return [
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=random.choice(replies))
        ]
