"""Bot commands modules interface"""

from typing import Optional, List

from sadbot.message import Message
from sadbot.bot_reply import BotAction

BOT_HANDLER_TYPE_NEW_USER = 0
BOT_HANDLER_TYPE_KEYBOARD_INPUT = 1
BOT_HANDLER_TYPE_MESSAGE = 2
BOT_HANDLER_TYPE_EDITED_MESSAGE = 3
BOT_HANDLER_TYPE_PICTURE = 4


class CommandInterface:
    """This is the interface for the bot commands, every bot command module must implement
    these functions"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the command output"""
