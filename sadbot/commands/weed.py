"""Weed bot command"""

from typing import Optional, List
import random

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class WeedBotCommand(CommandInterface):
    """This is the weed bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching lenovo commands"""
        return r".*([Ww][Aa][Nn][Tt]).*([Ww][Ee]{2}[Dd]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
        """Politely refuses weed while staying cool cause my brain already smooth"""
        replies = [
            "Thank you for the offer, but I'm good",
            "No, thank you, I'm fine",
            "No, thanks, my brain already smooth enough",
            "I shalt decline thine propitious offer of inhaling plantam cannabinacearum in my lungs quod I hitherto feel accomplished about the life of mine person.",
        ]
        return [BotReply(BOT_REPLY_TYPE_TEXT, reply_text=random.choice(replies))]
