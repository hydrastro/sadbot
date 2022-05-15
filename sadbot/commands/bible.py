"""Bible bot command"""

from typing import Optional, List
import json

import requests

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class BibleBotCommand(CommandInterface):
    """This is the Bible quote bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Bb][Ii][Bb][Ll][Ee])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns Bible quote"""
        if message is None or message.text is None:
            return None
        if len(message.text) < 8:
            return None
        verses = message.text[7:]
        verses = verses.replace(" ", "+")
        try:
            url = f"https://bible-api.com/{verses}"
            req = requests.get(url)
            body = req.json()
            output = ""
            for entry in body["verses"]:
                verse: dict = entry
                line = verse["book_name"]
                line += f' {str(verse["chapter"])}:{str(verse["verse"])} - '
                line += verse["text"]
                output += line + "\n"
            return [
                BotAction(
                    reply_type=BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text=output,
                )
            ]
        except (requests.ConnectionError, json.JSONDecodeError):
            return None
        return None
