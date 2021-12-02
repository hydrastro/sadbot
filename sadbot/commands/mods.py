"""Mods bot command"""

from typing import Optional, List
import logging

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
)
from sadbot.app import App


class ModsBotCommand(CommandInterface):
    """This is the mods bot command class"""

    def __init__(self, app: App):
        self.app = app

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the mods command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching mods commands"""
        return r".*(@([Mm][Oo][Dd][Ss])|((!|\.|/)[Rr][Ee][Pp][Oo][Rr][Tt])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Lists all moderators of a chat"""
        if message is None or message.text is None:
            return None
        administrators = self.app.get_chat_administrators(message.chat_id)
        if administrators is None:
            logging.error("Administrators not found.")
            return None
        if "result" not in administrators:
            return None
        text = "The list of moderators is:\n"
        for user in administrators["result"]:
            if "username" in user["user"]:
                text += f"- @{user['user']['username']}\n"
            elif "first_name" in user["user"]:
                text += f"- @{user['user']['first_name']}\n"
        return [
            BotAction(
                reply_text=text,
            )
        ]
