"""Bot action manager modules interface"""

from typing import Optional, List, Dict

from sadbot.message import Message


class ActionManagerInterface:
    """This is the interface for the bot event handlers"""

    def handle_callback(
        self,
        trigger_message: Message,
        sent_message: Optional[Message],
        callback_manager_info: Optional[Dict],
    ) -> None:
        """Sets the trigger message"""

    def get_trigger_message(self) -> Message:
        """Returns the message the manager is working on"""

    def get_message_and_actions(self) -> Optional[List[List]]:
        """Returns the manager's actions"""
