"""Bot commands modules interface"""

from typing import Optional, List, Protocol

from sadbot.message import Message
from sadbot.bot_action import BotAction

BOT_HANDLER_TYPE_NEW_USER = 0
BOT_HANDLER_TYPE_CALLBACK_QUERY = 1
BOT_HANDLER_TYPE_MESSAGE = 2
BOT_HANDLER_TYPE_EDITED_MESSAGE = 3
BOT_HANDLER_TYPE_PICTURE = 4
BOT_HANDLER_TYPE_DOCUMENT = 5


class CommandInterface(Protocol):
    """This is the interface for the bot commands, every bot command module must implement
    these functions"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the command output"""
