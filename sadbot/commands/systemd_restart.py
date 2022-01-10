"""Systemd service restart bot command"""

import random
from typing import Optional, List
import os

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT

class SystemdRestartBotCommand(CommandInterface):
    """This is the restart bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roll command"""
        return r"(\.[Rr][Ee][Ss][Tt][Aa][Rr][Tt]{2}).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Restarts the bot systemd service"""
        # Remember to allow this command in /etc/sudoers
        os.system("sudo service sadbot restart")
        return [BotAction(BOT_ACTION_TYPE_NONE)]
