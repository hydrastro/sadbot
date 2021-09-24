"""Get id bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.message_repository import MessageRepository


class GetIdBotCommand(CommandInterface):
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
        return r"((!|\.)([Gg][Ee][Tt][Ii][Dd]))(.*)?"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns a user id"""
        if message is None or message.text is None:
            return None
        user_id_to_find = None
        user_to_find = None
        if message.reply_id is not None:
            old_message = self.message_repository.get_message_from_id(message.reply_id)
            if old_message is not None:
                user_id_to_find = old_message.sender_id
                user_to_find = old_message.sender_name
        if len(message.text) > 7:
            message_text = message.text.split()
            if len(message_text) == 2:
                if user_id_to_find is None:
                    user_to_find = message_text[1].replace("@", "")
                    user_id_to_find = self.message_repository.get_user_id_from_username(
                        user_to_find
                    )
            if len(message_text) == 3:
                user_to_find = message_text[1].replace("@", "")
                user_id_to_find = self.message_repository.get_user_id_from_username(
                    user_to_find
                )
        if user_id_to_find is None:
            reply_text = "User not found"
            return None
        reply_text = f"{user_to_find} user id: {user_id_to_find}."
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
            ),
        ]
