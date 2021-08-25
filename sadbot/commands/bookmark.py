"""Bookmark bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class BookmarkBotCommand(CommandInterface):
    """This is the bookmark bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching bookmarks"""
        return r"#\w+"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the bookmarked reply"""
        if message is None or message.text is None:
            return None
        matching_message = Message(chat_id=message.chat_id, sender_id=message.sender_id)
        reply_message = self.message_repository.get_previous_message(
            matching_message, message.text
        )
        if reply_message is None:
            return None
        reply = "Yo, I found your bookmark"
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply,
                reply_to_message_id=reply_message.message_id,
            )
        ]
