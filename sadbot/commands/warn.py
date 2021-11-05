"""Warn bot command"""
import time
from typing import List, Optional, Tuple

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.bot_action import (
    BOT_ACTION_PRIORITY_HIGH,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BotAction,
)
from sadbot.chat_permissions import ChatPermissions
from sadbot.classes.permissions import Permissions
from sadbot.command_interface import BOT_HANDLER_TYPE_MESSAGE, CommandInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.classes.user_warnings import UserWarnings


def mute_time(count: int) -> Optional[Tuple[int, str]]:
    """Mute time for current count"""
    # <3 - no mute
    # 3 - 4 hours
    # 4 - 1 day
    # 5 - 3 days
    # >5 - permamute
    if count < 3:
        return None
    if count == 3:
        return (14400, "4 hours")
    if count == 4:
        return (86400, "1 day")
    if count == 5:
        return (259200, "3 days")
    return (0, "eternity")


class WarnBotCommand(CommandInterface):
    """This is the warn command class"""

    def __init__(
        self,
        app: App,
        message_repository: MessageRepository,
        permissions: Permissions,
        user_warnings: UserWarnings,
    ):
        """Initializes the warn command"""
        self.app = app
        self.message_repository = message_repository
        self.permissions = permissions
        self.user_warnings = user_warnings

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""
        return "([.]|[!]|[/])[wW][aA][rR][nN].*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        # pylint: disable=R0911
        """Returns the command output"""
        if message is None or message.text is None:
            return None
        warn_sender_id = None
        if message.reply_id is not None:
            warn_message = self.message_repository.get_reply_message(message)
            if warn_message is None:
                return None
            warn_sender_id = warn_message.sender_id
            warn_username = warn_message.sender_username
        else:
            text = message.text.split()
            if len(text) < 2:
                return None
            warn_username = text[1].replace("@", "")
            if warn_username is None:
                return None
            print(warn_username)
            warn_sender_id = self.message_repository.get_user_id_from_username(
                warn_username
            )
        if warn_sender_id is None:
            return None
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
                    reply_text="You don't have enough rights to warn, kiddo.",
                )
            ]
        timestamp = int(time.time()) - 604800
        self.user_warnings.insert_new_warn(
            message.chat_id, warn_sender_id, int(time.time())
        )
        count = self.user_warnings.get_warns_since_timestamp(
            message.chat_id, warn_sender_id, timestamp
        )
        mute = mute_time(count)
        if mute is None:
            reply_text = (
                f"{warn_username} has been successfully warned.\n"
                + f"The user has {count} {'warns' if count != 1 else 'warn'} in the last week"
            )
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text=reply_text,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
            ]
        username = "User" if warn_username is None else warn_username
        reply_text = (
            f"{username} has been successfully warned.\n"
            + f"The user has {count} {'warns' if count != 1 else 'warn'} in the last week.\n"
            + f"Because of the warnings, you are muted for {mute[1]}"
        )
        mute_permissions = ChatPermissions(
            False, False, False, False, False, False, False, False
        )
        until_date = int(time.time() + mute[0])
        mute_permissions.ban_until_date = until_date
        self.permissions.set_user_permissions(
            warn_sender_id, message.chat_id, mute_permissions
        )
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=warn_sender_id,
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
