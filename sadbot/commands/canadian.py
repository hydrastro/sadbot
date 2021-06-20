"""Leaf bot command"""

from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class CanadianBotCommand(CommandInterface):
    """This is the leaf bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"((!|\.)([Ll][Ee][Aa][Ff]|[Cc][Aa][Nn][Aa][Dd][Ii][Aa][Nn])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns leaf"""
        return BotReply(BOT_REPLY_TYPE_TEXT, reply_text="🇨🇦")
