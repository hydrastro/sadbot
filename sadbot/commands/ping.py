"""Ping bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class PingBotCommand(CommandInterface):
    """This is the ping bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Pp][Ii][Nn][Gg])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns pong"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text="pong")]
