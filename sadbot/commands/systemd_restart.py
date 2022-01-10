"""Systemd service restart bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.config import OWNER_ID


class SystemdRestartBotCommand(CommandInterface):
    """This is the restart bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roll command"""
        return r"(\.[Rr][Ee][Ss][Tt][Aa][Rr][Tt]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Restarts the bot systemd service"""
        if message is None:
            return None
        if message.sender_id != OWNER_ID:
            reply_text = "No."
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text="Restarting the bot.",
                reply_callback_manager_name="SystemdRestartManager",
            )
        ]
