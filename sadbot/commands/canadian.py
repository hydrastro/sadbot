"""Leaf bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class CanadianBotCommand(CommandInterface):
    """This is the leaf bot command class"""

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching leaf commands"""
        return r"((!|\.)([Ll][Ee][Aa][Ff]|[Cc][Aa][Nn][Aa][Dd][Ii][Aa][Nn])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns leaf"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text="🇨🇦")]
