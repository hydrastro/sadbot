"""Warn bot command"""
import time
from typing import List, Optional

from sadbot.app import App, CHAT_MEMBER_STATUS_ADMIN, CHAT_MEMBER_STATUS_CREATOR
from sadbot.bot_action import BOT_ACTION_TYPE_REPLY_TEXT, BotAction
from sadbot.command_interface import BOT_HANDLER_TYPE_MESSAGE, CommandInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.classes.user_warnings import UserWarnings


class WarnBotCommand(CommandInterface):
    """This is the warn command class"""

    def __init__(
        self,
        app: App,
        message_repository: MessageRepository,
        user_warnings: UserWarnings,
    ):
        """Initializes the warn command"""
        self.app = app
        self.message_repository = message_repository
        self.user_warnings = user_warnings

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex string that triggers this command"""
        return "([.]|[!]|[/])[wW][aA][rR][nN]"

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
        count = self.user_warnings.get_warns_since_timestamp(
            message.chat_id, warn_sender_id, timestamp
        )
        reply_text = f"""{warn_username} has been successfully warned.
The user has been warned {count} {'times' if count != 1 else 'time'} in the last week"""
        self.user_warnings.insert_new_warn(
            message.chat_id, warn_sender_id, int(time.time())
        )
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
