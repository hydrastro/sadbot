"""Remind me bot command"""
from typing import Optional, List
import sqlite3

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.functions import convert_to_seconds


class RemindMeBotCommand(CommandInterface):
    """This is the remind me command class"""

    def __init__(self, con: sqlite3.Connection):
        self.con = con

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Rr][Ee][Mm][Ii][Nn][Dd][Mm][Ee])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Pass to callback"""
        if message is None or message.text is None:
            return None
        if message.reply_id is None:
            return self.exit_message("Please select a message I have to remind you.")
        split = message.text.split()
        if len(split) < 2:
            return self.exit_message(
                "You have to specify when I shall remind you stuff."
            )
        callback_info = {"remind_time": convert_to_seconds(split[1])}
        reply_text = "Reminder set."
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_callback_manager_name="RemindMeManager",
                reply_callback_manager_info=callback_info,
            )
        ]

    @staticmethod
    def exit_message(reply_text: str) -> List[BotAction]:
        """Exits with a message"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
