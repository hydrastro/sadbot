"""Config bot command"""

from typing import Optional, List, Dict, Any
import logging

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message, MESSAGE_FILE_TYPE_PHOTO
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.classes.group_configs import GroupConfigs
from sadbot.classes.permissions import Permissions


class ConfigBotCommand(CommandInterface):
    """This is the config bot command class, it manages configs for other commands"""

    def __init__(
        self,
        app: App,
        message_repository: MessageRepository,
        group_configs: GroupConfigs,
        permissions: Permissions,
    ):
        self.app = app
        self.message_repository = message_repository
        self.group_configs = group_configs
        self.permissions = permissions

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching configs commands"""
        return r"((!|\.)([Ss][Ee][Tt]))\s.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Sets config"""
        if message is None or message.text is None:
            return None
        user_permissions = self.app.get_user_status_and_permissions(
            message.chat_id, message.sender_id
        )
        if user_permissions is None:
            logging.error("User permissions not found")
            return None
        if user_permissions[0] not in [
            CHAT_MEMBER_STATUS_ADMIN,
            CHAT_MEMBER_STATUS_CREATOR,
        ]:
            return self.exit_message("Stay in your place: you have no rights, kiddo.")
        reply_text = self.set_configs(message)
        return self.exit_message(reply_text)

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

    def set_rules(self, message: Message) -> str:
        """Sets rules and returns a result string"""
        if message.reply_id is None:
            return "You have to specify a message for the rules."
        rules_message = self.message_repository.get_message_from_id(message.reply_id)
        if rules_message is None:
            return "An error occured, the message was not found in the database."
        rules: Dict[str, Any] = {}
        if rules_message.text is not None:
            rules["text"] = rules_message.text
        if (
            rules_message.file_type == MESSAGE_FILE_TYPE_PHOTO
            and rules_message.file_id is not None
        ):
            photo = self.app.get_file_from_id(rules_message.file_id)
            if photo is not None:
                with open(
                    f"./sadbot/assets/rules/{message.chat_id}.jpg", "wb"
                ) as image_file:
                    image_file.write(photo)
                rules["photo"] = True
        self.group_configs.set_group_config(message.chat_id, "rules", rules)
        return "Group rules successfully updated."

    @staticmethod
    def exit_message(reply_text: str) -> Optional[List[BotAction]]:
        """Just returns a message with a specified text"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
