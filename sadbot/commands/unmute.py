"""Unmute bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.chat_helper import (
    ChatHelper,
    CHAT_HELPER_MEMBER_STATUS_ADMIN,
    CHAT_HELPER_MEMBER_STATUS_CREATOR,
)
from sadbot.permissions import Permissions
from sadbot.message_repository import MessageRepository
from sadbot.chat_helper import ChatHelper


class UnmuteBotCommand(CommandInterface):
    """This is the unmute bot command class"""

    def __init__(self, chat_helper: ChatHelper, message_repository: MessageRepository):
        self.chat_helper = chat_helper
        self.message_repository = message_repository

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
        user_id_to_unmute = None
        message_text = message.text.split()
        user_to_unmute = message_text[1].replace("@", "")
        user_id_to_unmute = self.message_repository.get_user_id_from_username(
            user_to_unmute
        )
        if user_id_to_unmute is None:
            return None
        user_permissions = self.chat_helper.get_user_permissions(
            message.chat_id, message.sender_id
        )
        if user_permissions is None:
            return None
        user_type = user_permissions[0]
        if user_type not in [
            CHAT_HELPER_MEMBER_STATUS_ADMIN,
            CHAT_HELPER_MEMBER_STATUS_CREATOR,
        ]:
            return None
        if (
            user_type != CHAT_HELPER_MEMBER_STATUS_CREATOR
            and not user_permissions[1].can_restrict_members
        ):
            return None
        unmute_permissions = self.chat_helper.get_chat_permissions(message.chat_id)
        reply_text = "User succesfully unmuted."
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=user_id_to_unmute,
                reply_permissions=unmute_permissions,
            ),
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text),
        ]
