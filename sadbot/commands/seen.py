"""Seen bot command"""

import datetime
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.functions import convert_time


class SeenBotCommand(CommandInterface):
    """This is the seen bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the seen command"""
        return r"(!|\.)([Ss][Ee]{2}[Nn])\s\w+"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Gets the reply"""
        if message is None or message.text is None:
            return None
        message.text = message.text.replace("@", "")
        username = message.text[6:]
        user_id = self.message_repository.get_user_id_from_username(username)
        if user_id is None:
            return None
        last_message = self.message_repository.get_user_last_message(
            user_id, message.chat_id
        )
        if (
            last_message is None
            or last_message.message_time == 0
            or last_message.message_time is None
        ):
            return None
        last_seen = datetime.datetime.fromtimestamp(last_message.message_time)
        time_ago = convert_time(last_message.message_time, True)
        reply = f"{username} was last seen {time_ago} (on {last_seen})"
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply)]
