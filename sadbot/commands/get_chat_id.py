"""Get chat id bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.message_repository import MessageRepository


class GetChatIdBotCommand(CommandInterface):
    """This is the get id bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the get id command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching get id commands"""
        return r"((!|\.)([Gg][Ee][Tt][Cc][Hh][Aa][Tt][Ii][Dd]))(.*)?"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the chat id"""
        if message is None:
            return None
        reply_text = f"{message.chat_id}"
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
            ),
        ]
