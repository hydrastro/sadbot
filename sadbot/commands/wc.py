"""Wordcount bot command"""

import functools
from typing import List, Optional

from sadbot.bot_action import BOT_ACTION_TYPE_REPLY_TEXT, BotAction
from sadbot.command_interface import BOT_HANDLER_TYPE_MESSAGE, CommandInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository


def foldl(func, acc, iterator):
    """Folds an iterator"""
    return functools.reduce(func, iterator, acc)


class WcBotCommand(CommandInterface):
    """This is the wc bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"[.]([wW][cC]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        if message is None:
            return None
        if message.text is None:
            return None
        reply_message = self.message_repository.get_reply_message(message)
        if reply_message is None or reply_message.text is None:
            return None
        text = reply_message.text
        line_count = len(text.splitlines())
        word_count = len(text.split())
        char_count = len(text)
        longest_line_count = foldl(lambda a, b: max(a, len(b)), 0, text.splitlines())
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=f"""Word count: {word_count}
                Line count: {line_count}
                Character count: {char_count}
                Longest line length: {longest_line_count}""",
            ),
        ]
