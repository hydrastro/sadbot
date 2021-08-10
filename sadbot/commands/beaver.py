"""Beaver bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class BeaverBotCommand(CommandInterface):
    """This is the beaver bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching sed command"""
        return r"(!|\.)([Ss][Ee]{2}[Tt][Hh][Ee]|[Bb][Ee][Aa][Vv][Ee][Rr]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Speaks the truth"""
        if message is None:
            return None
        beaver_user_id = 1_749_391_268
        beaver_message = self.message_repository.get_random_message_from_user(
            beaver_user_id, message.chat_id
        )
        if beaver_message is None or beaver_message.text is None:
            return None
        reply_text = f"Here's a quote from beaver:\n{beaver_message.text}"
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
