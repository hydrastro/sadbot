"""Hi I am bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class HiIAmBotCommand(CommandInterface):
    """This is the hi I am bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching hi I am commands"""
        return r"([Ii](\s[Aa][Mm]|'[Mm]))\s\w+"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns stuff"""
        if message is None or message.text is None:
            return None
        who = message.text.split()[-1]
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text=f"Hi {who}, I'm Real Human"
            )
        ]
