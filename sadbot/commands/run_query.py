"""Admin database query command"""

from typing import Optional, List

from sadbot.message_repository import MessageRepository
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.config import OWNER_ID


class RunQueryBotCommand(CommandInterface):
    """This is the run query bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"(!|\.)([Qq][Uu][Ee][Rr][Yy])\s.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Runs a query"""
        if message is None or message.text is None:
            return None
        if message.sender_id != OWNER_ID:
            reply_text = "No."
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
        if len(message.text) < 5:
            reply_text = "Invalid query"
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
        query = message.text[6:]
        reply = str(self.message_repository.run_query(query))
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply)]
