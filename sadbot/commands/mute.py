"""Mute bot command"""

from typing import Optional, List
import time
import logging

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_PRIORITY_HIGH,
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
    def handler_type(self) -> int:
        """Returns the type of event handled by the mute command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching mute commands"""
        return r"((!|\.|/)([Mm][Uu][Tt][Ee]))(.*)?"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Mutes a user"""
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
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text="You don't have enough rights to mute, kiddo.",
                )
            ]
        mute_permissions = ChatPermissions(
            False, False, False, False, False, False, False, False
        )
        user_to_mute = self.message_repository.get_target_user(message)
        until_date = 0
        # If replying to:
        # /mute [time]
        # If NOT replying to
        # /mute @username [time]
        splat = message.text.split()
        until_date = 0
        until_text = ""
        if message.reply_id is not None and len(splat) > 1:
            until_date = convert_to_seconds(splat[2])
            until_text = splat[1]
        elif len(splat) > 2:
            until_date = convert_to_seconds(splat[2])
            until_text = splat[2]
        if until_date < 30:  # because for telegram < 30 is forever lmao
            until_text = "ever, lmao"
        until_date += int(time.time())
        until_date += 2  # Delay for the api request and elaboration time
        if user_to_mute is None:
            return None
        mute_permissions.ban_until_date = until_date
        self.permissions.set_user_permissions(
            user_to_mute.user_id, message.chat_id, mute_permissions
        )
        user_to_mute = "User" if user_to_mute is None else user_to_mute
        reply_text = (
            f"{user_to_mute.user_username} has successfully been muted for{until_text}."
        )
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=user_to_mute.user_id,
                reply_permissions=mute_permissions,
                reply_restrict_until_date=until_date,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
