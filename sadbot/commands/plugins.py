"""Plugins bot command"""
from typing import Optional, List
import logging

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.message import Message
from sadbot.classes.group_configs import GroupConfigs
from sadbot.classes.permissions import Permissions
from sadbot.classes.plugins_keyboard import PluginsKeyboard


class PluginsBotCommand(CommandInterface):
    """This is the config bot command class, it manages configs for other commands"""

    def __init__(
        self,
        app: App,
        group_configs: GroupConfigs,
        permissions: Permissions,
        plugins_keyboard: PluginsKeyboard,
    ):
        self.app = app
        self.group_configs = group_configs
        self.permissions = permissions
        self.plugins_keyboard = plugins_keyboard

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching configs commands"""
        return r"(!|\.|/)([Pp][Ll][Uu][Gg][Ii][Nn][Ss])"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Return the keyboard as a BotAction"""
        if message is None or message.text is None:
            return None
        user_permissions = self.app.get_user_status_and_permissions(
            message.chat_id, message.sender_id
        )
        if user_permissions is None:
            logging.error("User permissions not found.")
            return None
        user_type = user_permissions[0]
        if user_type not in [CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR] or (
            user_type != CHAT_MEMBER_STATUS_CREATOR
            and not user_permissions[1].can_restrict_members
        ):
            # pass
            return self.exit_message(
                "You don't have enough rights to handle plugins, kiddo."
            )
        inline_keyboard = self.plugins_keyboard.get_keyboard(message.chat_id, 0)
        reply_text = (
            f"Here you can manage the bot commands for the chat '{message.chat_name}':"
        )
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text="Sup boss, I sent you the control panel in our private chat.",
            ),
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_inline_keyboard=inline_keyboard,
                reply_chat_id=message.sender_id,
            ),
        ]

    @staticmethod
    def exit_message(reply_text: str) -> Optional[List[BotAction]]:
        """Just returns a message with a specified text"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
