"""Git pull bot command"""

from typing import Optional, List
import subprocess

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.config import OWNER_ID


class GitPullBotCommand(CommandInterface):
    """This is the git pull bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roll command"""
        return r"(\.([Gg][Ii][Tt](\s+)?)?[Pp][Uu][Ll]{2}).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Restarts the bot systemd service"""
        if message is None:
            return None
        if message.sender_id != OWNER_ID:
            reply_text = "No."
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
        result = subprocess.check_output("git pull", shell=True, encoding="UTF-8")
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=result)]
