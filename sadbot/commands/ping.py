"""Ping bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class PingBotCommand(CommandInterface):
    """This is the ping bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Pp][Ii][Nn][Gg])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
        """Returns pong"""
        return [BotReply(BOT_REPLY_TYPE_TEXT, reply_text="pong")]
