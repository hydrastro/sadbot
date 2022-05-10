"""Plugins callback bot command"""
from typing import Optional, List
import logging

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_CALLBACK_QUERY
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
    BOT_ACTION_TYPE_EDIT_MESSAGE_TEXT,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.classes.group_configs import GroupConfigs
from sadbot.classes.plugins_keyboard import PluginsKeyboard


class PluginsCallbackBotCommand(CommandInterface):
    """This is the plugins callback query (reply) class"""

    def __init__(
        self, app: App, plugins_keyboard: PluginsKeyboard, group_configs: GroupConfigs
    ):
        self.app = app
        self.plugins_keyboard = plugins_keyboard
        self.group_configs = group_configs

    @property
    def handler_type(self) -> int:
        return BOT_HANDLER_TYPE_CALLBACK_QUERY

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching plugins (in the callback query data)"""
        return r"pk.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Handles the plugins keyboard"""
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
            return [
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text="Yo you don't have permissions kiddo.",
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
            ]
        callback_data = message.text.split(".")
        chat_id = int(callback_data[1])
        current_page = int(callback_data[2])
        callback_reply_message = ""
        # pk.(chat_id).{current_page}.
        #                             command.(command).info
        #                             command.(command).(action=enable/disable)
        #                             page.current
        #                             page.(number)
        #                             enable (all)
        #                             disable (all)
        if callback_data[3] == "c":
            if callback_data[5] == "e":
                self.plugins_keyboard.enable_plugin(chat_id, callback_data[4])
                callback_reply_message = "Command successfully enabled."
            elif callback_data[5] == "d":
                self.plugins_keyboard.disable_plugin(chat_id, callback_data[4])
                callback_reply_message = "Command successfully disabled."
            elif callback_data[5] == "i":
                # TODO pylint: disable=fixme
                callback_reply_message = "Yo"
            else:
                callback_reply_message = "Yo wtf"
        elif callback_data[3] == "p":
            if callback_data[4].isnumeric():
                page = int(callback_data[4]) + 1
                callback_reply_message = f"Going to page {page}"
                inline_keyboard = self.plugins_keyboard.get_keyboard(
                    message, int(callback_data[4])
                )
                return [
                    BotAction(
                        BOT_ACTION_TYPE_EDIT_MESSAGE_TEXT,
                        reply_target_message_id=message.reply_id,
                        reply_text="Here you can enable or disable the bot commands:",
                        reply_inline_keyboard=inline_keyboard,
                        reply_priority=BOT_ACTION_PRIORITY_HIGH,
                    ),
                    BotAction(
                        BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                        reply_callback_query_id=message.message_id,
                        reply_text=callback_reply_message,
                        reply_priority=BOT_ACTION_PRIORITY_HIGH,
                    ),
                ]
            callback_reply_message = "Yo wassup"
        elif callback_data[3] == "e":
            self.plugins_keyboard.enable_all_plugins(chat_id)
            callback_reply_message = "Commands successfully enabled."
        elif callback_data[3] == "d":
            self.plugins_keyboard.disable_all_plugins(chat_id)
            callback_reply_message = "Commands successfully disabled."
        inline_keyboard = self.plugins_keyboard.get_keyboard(message, current_page)
        return [
            BotAction(
                BOT_ACTION_TYPE_EDIT_MESSAGE_TEXT,
                reply_target_message_id=message.reply_id,
                reply_text="Here you can enable or disable the bot commands:",
                reply_inline_keyboard=inline_keyboard,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                reply_callback_query_id=message.message_id,
                reply_text=callback_reply_message,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
