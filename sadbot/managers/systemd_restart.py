"""Here is the systemd restart manager"""
from typing import Optional, List, Dict
import os

from sadbot.message import Message
from sadbot.action_manager_interface import ActionManagerInterface


class SystemdRestartManager(ActionManagerInterface):
    """Handles the bot restart"""

    def handle_callback(
        self,
        trigger_message: Message,
        sent_message: Optional[Message],
        callback_manager_info: Optional[Dict],
    ) -> None:
        """Handles the callback and restarts the bot"""
        # Remember to allow this command in /etc/sudoers
        os.system("sudo service sadbot restart")

    @staticmethod
    def get_actions() -> Optional[List[List]]:
        """Returns bot actions"""
        return None
