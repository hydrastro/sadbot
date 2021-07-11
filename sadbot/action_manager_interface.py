"""Bot action manager modules interface"""

from typing import Optional, List, Dict

from sadbot.bot_action import BotAction
from sadbot.message import Message


class ActionManagerInterface:
    """This is the interface for the bot event handlers"""

    def set_trigger_message(self, trigger_message: Message) -> None:
        """Sets the trigger message"""

    def set_sent_message(self, sent_message: Message) -> None:
        """Sets the sent message"""

    def set_callback_manager_info(self, callback_manager_info: Dict) -> None:
        """Sets the callback manager info"""

    @property
    def is_active(self) -> bool:
        """Returns the status of the command: if it False the current instance is destroyed"""

    def get_message(self) -> Message:
        """Returns the message the manager is working on"""

    def get_reply(self) -> Optional[List[BotAction]]:
        """Returns the manager's actions"""
