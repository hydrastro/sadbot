"""Bot commands modules interface"""

from typing import Optional

from sadbot.message import Message
from sadbot.bot_reply import BotReply


class CommandInterface:
    """This is the interface for the bot commands, every bot command module must implement
    these functions"""

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Returns the command output"""
