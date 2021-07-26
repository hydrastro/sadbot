"""Mute bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER
from sadbot.chat_helper import ChatHelper, CHAT_HELPER_MEMBER_STATUS_ADMIN, CHAT_HELPER_MEMBER_STATUS_CREATOR
from sadbot.permissions import Permissions
from sadbot.functions import safe_cast


class MuteBotCommand(CommandInterface):
    """This is the leaf bot command class"""

    def __init__(self, chat_helper: ChatHelper):
        self.chat_helper = chat_helper

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
        until_date = message.text[5:]
        until_date = safe_cast(until_date, int, None)
        user_permissions = self.chat_helper.get_user_permissions(message.chat_id, message.sender_id)
        if user_permissions is None:
            return None
        user_type = user_permissions[0]
        if user_type not in [CHAT_HELPER_MEMBER_STATUS_ADMIN, CHAT_HELPER_MEMBER_STATUS_CREATOR]:
            return None
        if  user_type != CHAT_HELPER_MEMBER_STATUS_CREATOR or not user_permissions[1].can_restrict_members:
            return None
        mute_permissions = self.chat_helper.get_list_dict_permissions(Permissions(False, False, False, False, False, False, False, False))
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_ban_user_id=message.reply_id,
                reply_permissions=mute_permissions,
                reply_restrict_until_date=until_date,
            )
        ]
