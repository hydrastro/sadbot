"""Roulette bot command"""

import re
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.config import REVOLVER_CHAMBERS
from sadbot.functions import safe_cast
from sadbot.bot_action import BotAction
from sadbot.classes.revolver import Revolver


class RouletteBotCommand(CommandInterface):
    """This is the roulette bot command class"""

    def __init__(self, revolver: Revolver):
        """Initializes the roulette bot command class"""
        self.revolver = revolver

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roulette command"""
        return (
            r"(\.[Rr]([Oo][Uu][Ll][Ee][Tt]{2}[Ee]|[Ee][Ll][Oo][Aa][Dd]|[Ee][Vv]"
            r"[Oo][Ll][Vv][Ee][Rr]\s[0-9]+)).*"
        )

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Plays the Russian roulette"""
        if message is None or message.text is None:
            return None
        reload_regex = re.compile(r"(\.[Rr][Ee][Ll][Oo][Aa][Dd]).*")
        if re.fullmatch(reload_regex, message.text):
            bullets = message.text[7:]
            bullets = bullets.replace(" ", "")
            int_bullets = safe_cast(bullets, int, bullets)
            return self.revolver.reload(message.chat_id, int_bullets)
        revolver_regex = re.compile(r"(\.[Rr][Ee][Vv][Oo][Ll][Vv][Ee][Rr]\s[0-9]+)")
        if re.fullmatch(revolver_regex, message.text):
            split = message.text[9:].split()
            capacity = safe_cast(split[0], int, REVOLVER_CHAMBERS)
            int_bullets = 1
            if len(split) > 1:
                int_bullets = safe_cast(split[1], int, 1)
            return self.revolver.revolver(message.chat_id, capacity, int_bullets)
        return self.revolver.shoot(message.chat_id)
