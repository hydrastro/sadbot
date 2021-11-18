"""Plugins callback bot command"""
from typing import Optional, List
import random
import logging

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_CALLBACK_QUERY
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_BAN_USER,
    BOT_ACTION_TYPE_UNBAN_USER,
    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.app import App
from sadbot.classes.captcha import Captcha
from sadbot.classes.permissions import Permissions
from sadbot.classes.group_configs import GroupConfigs
from sadbot.commands.plugins import PluginsBotCommand


class PluginsCallbackBotCommand(CommandInterface):
    """This is the plugins callback query (reply) class"""

    def __init__(self, plugins_command: PluginsBotCommand):
        self.plugins_command = plugins_command

    @property
    def handler_type(self) -> int:
        return BOT_HANDLER_TYPE_CALLBACK_QUERY

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching plugins (in the callback query data)"""
        return r"plugins.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Handles the plugins keyboard"""
        if message is None or message.text is None:
            return None
        callback_data = message.text.rsplit("-", 3)
        chat_id = callback_data[0].split("-", 1)
        current_page = callback_data[1]
        command = callback_data[2]
        callback_reply_message = ""
        if callback_data[2] == "command":
            pass
        elif callback_data[2] == "page":
            if callback_data[3].isnumeric():
                 callback_reply_message = "Going to page " + callback_data[2]
                 # TODO: send keyboard again
            else:
                callback_reply_message = "Yo"
        elif callback_data[2] == "enable":
            pass
        elif callback_data[2] == "disable":
            pass
        callback_data_split = callback_data[0].split("-", 1) # 
        captcha_id = callback_data_split[1]
        captcha_sender_id = captcha_id.split(".")[1]
        if captcha_sender_id != str(message.sender_id):
            not_yours = self.get_not_your_captcha_reply()
            return [
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text=not_yours,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
            ]
        captcha_text = self.captcha.get_captcha_from_id(captcha_id)
        self.captcha.delete_captcha(captcha_id)
        if captcha_text is None:
            logging.warning("Error: captcha not found in the database.")
            return None
        if callback_data[1] != captcha_text:
            return self.kick_user(message, captcha_id, True, message.reply_id)
        new_user = (
            message.sender_name
            if message.sender_username is None
            else f"@{message.sender_username}"
        )
        self.captcha.delete_captcha(captcha_id)
        welcome_reply = self.get_welcome_reply(new_user)
        permissions = self.permissions.get_user_permissions(
            message.sender_id, message.chat_id
        )
        if permissions is None:
            permissions = self.app.get_chat_permissions(message.chat_id)
        replies = [
            BotAction(
                BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                reply_callback_query_id=message.message_id,
                reply_text=self.get_correct_captcha_callback_reply(),
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_ban_user_id=message.sender_id,
                reply_delete_message_id=message.reply_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_permissions=permissions,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
        rules = self.group_configs.get_group_config(message.chat_id, "rules")
        if rules is not None and "rules" in rules:
            if "text" in rules["rules"]:
                if rules["rules"]["text"] is not None:
                    welcome_reply += "\n" + rules["rules"].get("text", "")
            if "photo" in rules["rules"] and rules["rules"]["photo"] is not None:
                try:
                    with open(
                        f"./sadbot/data/rules/{message.chat_id}.jpg", mode="rb"
                    ) as reply_image_file:
                        reply_image = reply_image_file.read()
                except FileNotFoundError:
                    replies += [
                        BotAction(
                            BOT_ACTION_TYPE_REPLY_TEXT,
                            reply_text="An error occured retrieving the group rules",
                        )
                    ]
                replies += [
                    BotAction(
                        BOT_ACTION_TYPE_REPLY_IMAGE,
                        reply_text=welcome_reply,
                        reply_image=reply_image,
                    )
                ]
            else:
                replies += [
                    BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=welcome_reply)
                ]
        return replies

    def kick_user(
        self,
        message: Message,
        captcha_id: str,
        answer_callback_query: Optional[bool] = True,
        sent_message_to_delete_id: Optional[int] = None,
    ) -> List[BotAction]:
        """Kicks a user from a chat"""
        if message is None:
            return None
        new_user = (
            message.sender_name
            if message.sender_username is None
            else f"@{message.sender_username}"
        )
        kick_text_replies = [
            "Begone bot",
            "lol i knew it was a bot",
            "There's space for only one bot here, and that's me",
            "Wrong captcha",
            "Oopsie-whooppsie *blushes* owo s s s-owrry but the cawpthwa yowu enterwed was nwot "
            "corrwect ;-; *starts twerking*",
            "Get rekt",
        ]
        kick_text = random.choice(kick_text_replies)
        kick_text += f"\n(I kicked {new_user} (id {message.sender_id}))"
        self.captcha.delete_captcha(captcha_id)
        replies = []
        if answer_callback_query:
            replies.append(
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text=kick_text,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
            )
        replies += [
            BotAction(
                BOT_ACTION_TYPE_BAN_USER,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=kick_text,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_UNBAN_USER,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
        permissions = self.permissions.get_user_permissions(
            message.sender_id, message.chat_id
        )
        if permissions is None:
            permissions = self.app.get_chat_permissions(message.chat_id)
        replies += [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_permissions=permissions,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
        if sent_message_to_delete_id is not None:
            replies += [
                BotAction(
                    BOT_ACTION_TYPE_DELETE_MESSAGE,
                    reply_delete_message_id=sent_message_to_delete_id,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
            ]
        return replies
