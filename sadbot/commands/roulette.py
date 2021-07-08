"""Roulette bot command"""

import re
from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.config import REVOLVER_CHAMBERS, REVOLVER_BULLETS
from sadbot.functions import safe_cast
from sadbot.bot_reply import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.classes.revolver import Revolver


class RouletteBotCommand(CommandInterface):
    """This is the roulette bot command class"""

    def __init__(self):
        """Initializes the roulette bot command class"""
        self.bullets = REVOLVER_BULLETS
        self.revolvers = {}

    @property
    def handler_type(self) -> str:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roulette command"""
        return r"(\.[Rr]([Oo][Uu][Ll][Ee][Tt]{2}[Ee]|[Ee][Ll][Oo][Aa][Dd]|[Ee][Vv]\
        [Oo][Ll][Vv][Ee][Rr]\s[0-9]+)).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Plays the Russian roulette"""
        if message.chat_id not in self.revolvers:
            revolver = Revolver(REVOLVER_CHAMBERS)
            revolver.reload(self.bullets)
            self.revolvers.update({message.chat_id: revolver})
        revolver = self.revolvers[message.chat_id]
        if re.fullmatch(re.compile(r"(\.[Rr][Ee][Ll][Oo][Aa][Dd]).*"), message.text):
            bullets = message.text[7:]
            bullets = bullets.replace(" ", "")
            bullets = safe_cast(bullets, int, self.bullets)
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT, reply_text=revolver.reload(bullets)
                )
            ]
        if re.fullmatch(
            re.compile(r"(\.[Rr][Ee][Vv][Oo][Ll][Vv][Ee][Rr]\s[0-9]+)"), message.text
        ):
            capacity = message.text[9:]
            capacity = capacity.replace(" ", "")
            capacity = safe_cast(capacity, int, REVOLVER_CHAMBERS)
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text=revolver.set_capacity(capacity)
                    + revolver.reload(self.bullets),
                )
            ]
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=revolver.shoot())]
