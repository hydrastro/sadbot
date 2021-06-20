"""Letsdo bot command"""

from typing import Optional

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_TEXT


class LetsdoBotCommand(CommandInterface):
    """This is the letsdo bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching letsdo commands"""
        return r"((!|\.)([Ll][Ee][Tt][Ss][Dd][Oo]\s+\w+))"

    def get_reply(self, message: Optional[Message] = None) -> Optional[BotReply]:
        """Returns letsdo"""
        this = message.text[8:]
        this = (
            f"let's do {this}! {this} {this} toe "
            f"{this} banana fanna foe f{this[1:]} "
            f"me my moe m{this[1:]}, {this}"
        )
        return BotReply(BOT_REPLY_TYPE_TEXT, reply_text=this)
