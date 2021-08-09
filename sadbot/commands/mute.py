"""Mute bot command"""

from typing import Optional, List
import time

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.chat_permissions import ChatPermissions
from sadbot.message_repository import MessageRepository
from sadbot.functions import convert_to_seconds
from sadbot.classes.permissions import Permissions


class MuteBotCommand(CommandInterface):
    """This is the leaf bot command class"""

    def __init__(
        self, app: App, message_repository: MessageRepository, permissions: Permissions
    ):
        self.app = app
        self.message_repository = message_repository
        self.permissions = permissions

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"((!|\.|/)([Mm][Uu][Tt][Ee])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Mutes a user"""
        user_id_to_mute = None
        until_date = None
        if message.reply_id is not None:
            user_id_to_mute = self.message_repository.get_user_id_from_message_id(
                message.reply_id
            )
        if len(message.text) > 5:
            message_text = message.text.split()
            if len(message_text) == 2:
                if user_id_to_mute is None:
                    user_to_mute = message_text[1].replace("@", "")
                    user_id_to_mute = self.message_repository.get_user_id_from_username(
                        user_to_mute
                    )
                else:
                    until_date = convert_to_seconds(message_text[1])
            if len(message_text) == 3:
                user_to_mute = message_text[1].replace("@", "")
                user_id_to_mute = self.message_repository.get_user_id_from_username(
                    user_to_mute
                )
                until_date = convert_to_seconds(message_text[2])
        if until_date is not None:
            until_date += int(time.time())
        if user_id_to_mute is None:
            return None
        user_permissions = self.app.get_user_status_and_permissions(
            message.chat_id, message.sender_id
        )
        if user_permissions is None:
            return None
        user_type = user_permissions[0]
        if user_type not in [CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR,] or (
            user_type != CHAT_MEMBER_STATUS_CREATOR
            and not user_permissions[1].can_restrict_members
        ):
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text="You don't have enough rights to mute, kiddo.",
                )
            ]
        mute_permissions = ChatPermissions(
            False, False, False, False, False, False, False, False
        )
        self.permissions.set_user_permissions(
            user_id_to_mute, message.chat_id, mute_permissions, until_date
        )
        user_string = message.sender_name
        if message.sender_username is not None:
            user_string = "@" + message.sender_username
        reply_text = f"{user_string} has successfully been muted."
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=user_id_to_mute,
                reply_permissions=mute_permissions,
                reply_restrict_until_date=until_date,
            ),
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text),
        ]
