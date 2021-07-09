"""Bot action manager modules interface"""

from typing import Optional, List

from sadbot.bot_action import BotAction
from sadbot.message import Message


class ActionManagerInterface:
    """This is the interface for the bot event handlers"""

    @property
    def is_active(self) -> bool:
        """Returns the status of the command: if it False the current instance is destroyed"""

    def get_message(self) -> Message:
        """Returns the message the manager is working on"""

    def get_reply(self) -> Optional[List[BotAction]]:
        """Returns the manager's actions"""
