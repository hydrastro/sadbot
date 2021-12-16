"""Bible bot command"""

from typing import Optional, List

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
        verse = message.text[7:]
        verse.strip()
        print(verse)
        with open(
            "./sadbot/assets/bible/bible.txt", mode="r", encoding="utf-8"
        ) as bible:
            for line in bible:
                if line.startswith(verse):
                    return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=line)]
        return None
