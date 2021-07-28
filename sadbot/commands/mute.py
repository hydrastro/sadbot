"""Mute bot command"""

from typing import Optional, List
import time

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER
from sadbot.chat_helper import ChatHelper, CHAT_HELPER_MEMBER_STATUS_ADMIN, CHAT_HELPER_MEMBER_STATUS_CREATOR
from sadbot.permissions import Permissions
from sadbot.message_repository import MessageRepository
from sadbot.functions import safe_cast, convert_to_seconds


class MuteBotCommand(CommandInterface):
    """This is the leaf bot command class"""

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
        return r"((!|\.|/)([Mm][Uu][Tt][Ee])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Mutes a user"""
        user_id_to_mute = None
        until_date = None
        if message.reply_id is not None:
            user_id_to_mute = self.message_repository.get_user_id_from_message_id(message.reply_id)
        if len(message.text) > 5:
            message_text = message.text.split()
            if len(message_text) == 2:
                if user_id_to_mute is None:
                    user_to_mute = message_text[1].replace("@", "")
                    user_id_to_mute = self.message_repository.get_user_id_from_username(user_to_mute)
                else:
                    until_date = convert_to_seconds(message_text[1])
            if len(message_text) == 3:
                user_to_mute = message_text[1].replace("@", "")
                user_id_to_mute = self.message_repository.get_user_id_from_username(user_to_mute)
                until_date = convert_to_seconds(message_text[2])
        if until_date is not None:
            until_date += time.time()
        if user_id_to_mute is None:
            return None
        user_permissions = self.chat_helper.get_user_permissions(message.chat_id, message.sender_id)
        if user_permissions is None:
            return None
        user_type = user_permissions[0]
        if user_type not in [CHAT_HELPER_MEMBER_STATUS_ADMIN, CHAT_HELPER_MEMBER_STATUS_CREATOR]:
            return None
        if user_type != CHAT_HELPER_MEMBER_STATUS_CREATOR and not user_permissions[1].can_restrict_members:
            return None
        mute_permissions = self.chat_helper.get_list_dict_permissions(Permissions(False, False, False, False, False, False, False, False))
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=user_id_to_mute,
                reply_permissions=mute_permissions,
                reply_restrict_until_date=until_date,
            )
        ]
