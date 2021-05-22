"""Bot commands modules interface"""

from typing import Optional

from sadbot.message import Message


class CommandsInterface:
    """This is the interface for the bot commands, every bot command module must implement
    these functions"""

    #    def __init__(self):
    #        """Initializes the command class"""

    def get_regex(self) -> str:
        """Returns the regex string that triggers this command"""

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns the command output"""
