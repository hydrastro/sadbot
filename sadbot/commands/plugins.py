"""Plugins bot command"""

import glob
from os.path import dirname, basename, isfile, join
from typing import Optional, List, Dict, Any
import logging
from math import ceil

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message, MESSAGE_FILE_TYPE_PHOTO
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.classes.group_configs import GroupConfigs
from sadbot.classes.permissions import Permissions


class PluginsBotCommand(CommandInterface):
    """This is the config bot command class, it manages configs for other commands"""

    def __init__(
        self,
        app: App,
        group_configs: GroupConfigs,
        permissions: Permissions,
    ):
        self.commands = []
        for command_name in [basename(f)[:-3] for f in glob.glob(join(dirname(__file__), "*.py")) if isfile(f)]:
            if command_name == "__init__":
                continue
            self.commands.append(command_name)
        self.app = app
        self.group_configs = group_configs
        self.permissions = permissions

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching configs commands"""
        return r"(!|\.|/)([Pp][Ll][Uu][Gg][Ii][Nn][Ss])"

    def get_keyboard(self, message: Message, current_page: int) -> List[BotAction]:
        """Displays the available plugins in a keyboard"""
        keyboard_data = []
        callback_prefix = f"plugins-{message.chat_id}-{message.sender_id}"
        page_columns = 2
        page_rows = 6
        elements_per_page = page_columns * page_rows
        max_pages = ceil(len(self.commands) / elements_per_page)
        print(len(self.commands))
        for i in range((current_page) * elements_per_page, min((current_page + 1) * elements_per_page, len(self.commands))):
            if True:
                command_status = "✅" # green
                command_action = "disable"
            else:
                command_action = "❌" # red
                command_action = "enable"
            keyboard_data.append({"text": self.commands[i].title(), "callback_data": f"{callback_prefix}-command-{self.commands[i]}-info"})
            keyboard_data.append({"text": command_status, "callback_data": f"{callback_prefix}-command-{self.commands[i]}-{command_action}"})
        keyboard_data = [keyboard_data[n:n + page_columns * 2] for n in range(0, len(keyboard_data), page_columns * 2)]
        keyboard_data = keyboard_data
        keyboard_data.append([{"text": "Previous", "callback_data": f"{callback_prefix}-page-{current_page - 1}"},
                              {"text": f"{current_page + 1}/{max_pages}", "callback_data": f"{callback_prefix}-page-current"},
                              {"text": "Next", "callback_data": f"{callback_prefix}-page-{current_page + 1}"}])
        keyboard_data.append([{"text": "Enable all", "callback_data": f"{callback_prefix}-enable"},
                              {"text": "Disable all", "callback_data": f"{callback_prefix}-disable"}])
        inline_keyboard = keyboard_data
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Here you can enable or disable the bot commands:", reply_inline_keyboard=inline_keyboard, reply_callback_manager_name="PluginsManager")]

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Return the keyboard as a BotAction"""
        if message is None or message.text is None:
            return None
        # todo: check if user is admin
        return self.get_keyboard(message, 0)

    def set_configs(self, message: Message) -> str:
        """Sets configs and returns a reply string"""
        if message.text is None:
            return "An error occured"
        split = message.text.split()
        if len(split) < 2:
            return "Please specify your configs."
        reply_text = "Error: specified setting not found."
        if split[1] == "rules":
            reply_text = self.set_rules(message)
        return reply_text

    @staticmethod
    def exit_message(reply_text: str) -> Optional[List[BotAction]]:
        """Just returns a message with a specified text"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
2
