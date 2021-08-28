"""Sed bot command"""

import re
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class SedBotCommand(CommandInterface):
    """This is the sed bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching sed command"""
        return r"s/.*/.*[/g]*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Performs the sed command on a given message"""
        if message is None or message.text is None:
            print("RETURN 0")
            return None
        replace_all = False
        text = message.text
        if text.endswith("/"):
            text = text[:-1]
        if text.endswith("/g") and (text.count("/") > 2):
            replace_all = True
            text = text[:-2]
        first_split = text.split("/", 1)
        second_split = ["s"]
        second_split += first_split[1].rsplit("/", 1)
        if len(second_split) != 3:
            print("RETURN 1")
            return None
        old = second_split[1]
        new = second_split[2]
        if message.reply_id is not None:
            reply_message = self.message_repository.get_message_from_id(
                message.reply_id
            )
        else:
            matching_message = Message(chat_id=message.chat_id)
            reply_message = self.message_repository.get_previous_message(
                matching_message, old
            )
        if reply_message is None or reply_message.text is None:
            return None
        try:
            max_replace = 1
            if replace_all:
                max_replace = len(reply_message.text)
        except re.error:
            return None
        reply = re.sub(old, new, reply_message.text, max_replace)
        reply = "<" + reply_message.sender_name + ">: " + reply
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply)]
