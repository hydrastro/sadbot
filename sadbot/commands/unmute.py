"""Unmute bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.app import (
    App,
    CHAT_MEMBER_STATUS_ADMIN,
    CHAT_MEMBER_STATUS_CREATOR,
)
from sadbot.message_repository import MessageRepository
from sadbot.classes.permissions import Permissions


class UnmuteBotCommand(CommandInterface):
    """This is the unmute bot command class"""

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
        return r"((!|\.|/)([Uu][Nn][Mm][Uu][Tt][Ee]))\s+.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Unmutes a user"""
        message_text = message.text.split()
        user_to_unmute = message_text[1].replace("@", "")
        user_id_to_unmute = self.message_repository.get_user_id_from_username(
            user_to_unmute
        )
        if user_id_to_unmute is None:
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
                    reply_text="You don't have enough rights to unmute, kiddo.",
                )
            ]
        unmute_permissions = self.app.get_chat_permissions(message.chat_id)
        self.permissions.delete_user_permissions(message.chat_id, message.sender_id)
        reply_text = "User successfully unmuted."
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=user_id_to_unmute,
                reply_permissions=unmute_permissions,
            ),
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text),
        ]
