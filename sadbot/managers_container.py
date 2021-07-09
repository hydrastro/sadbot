"""Bot action manager modules container"""

from typing import Optional, List

from sadbot.message import Message
from sadbot.bot_action import BotAction


class ActionManagerContainer:
    """This is the container for the bot event handlers"""

    def __init__(self) -> None:
        self.managers = {}

    def dispatch_manager(self, class_id: str, manager_class) -> None:
        """Dispatches a new manager"""
        self.managers.update({class_id: manager_class})

    def get_managers_actions(self) -> Optional[List[List]]:
        """Returns the managers actions or kills them"""
        actions = []
        inactive_managers = []
        for manager in self.managers:
            if not self.managers[manager].is_active:
                inactive_managers.append(manager)
                continue
            temp = self.managers[manager].get_reply()
            if temp:
                actions.append([self.managers[manager].get_message(), temp])
        for manager in inactive_managers:
            del self.managers[manager]
        if not actions:
            return None
        return actions
