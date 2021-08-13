"""Kick bot command"""

from typing import Optional, List

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_BAN_USER,
    BOT_ACTION_TYPE_UNBAN_USER,
    BOT_ACTION_PRIORITY_HIGH,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.message_repository import MessageRepository


class KickBotCommand(CommandInterface):
    """This is the kick bot command class"""

    def __init__(self, app: App, message_repository: MessageRepository):
        self.app = app
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"((!|\.|/)([Kk][Ii][Cc][Kk]))\s+.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Kicks a user"""
        if message is None or message.text is None:
            return None
        ban_user_id = None
        ban_username = None
        if message.reply_id is not None:
            ban_user_id = self.message_repository.get_user_id_from_message_id(
                message.reply_id
            )
        if ban_user_id is None:
            message_text = message.text.split()
            ban_username = message_text[1].replace("@", "")
            ban_user_id = self.message_repository.get_user_id_from_username(
                ban_username
            )
        if ban_user_id is None:
            return None
        reply_text = "User successfully kicked."
        user_permissions = self.app.get_user_status_and_permissions(
            message.chat_id, message.sender_id
        )
        if user_permissions is None:
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
        if ban_user_id is not None:
            reply_text = f"{ban_username} has successfully been kicked."
        return [
            BotAction(
                BOT_ACTION_TYPE_BAN_USER,
                reply_ban_user_id=ban_user_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_UNBAN_USER,
                reply_ban_user_id=ban_user_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text),
        ]
