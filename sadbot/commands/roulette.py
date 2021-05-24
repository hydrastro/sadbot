"""Roulette bot command"""

import random
import re

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.config import REVOLVER_CHAMBERS, REVOLVER_BULLETS
from sadbot.functions import safe_cast


class Revolver:
    """This is the revolver class"""
    def __init__(self, capacity: int) -> None:
        """Initializes a revolver"""
        self.capacity = capacity
        self.drum = [0] * self.capacity
        self.fired = 0

    def set_capacity(self, capacity: int) -> str:
        """Changes the revolver's capacity"""
        self.__init__(capacity)
        return "Changed revolver capacity. "

    def reload(self, bullets: int) -> str:
        """Reoloads the revolver bullets"""
        if bullets >= self.capacity:
            return "There are too many bullets, y'all would be dead lmao"
        for i in range(0, bullets):
            self.drum[i] = 1
        random.shuffle(self.drum)
        self.fired = 0
        return "Reloaded!"

    def shoot(self) -> str:
        """Shoots"""
        if self.fired > self.capacity - 1:
            return "No more bullets, you have to .reload"
        self.fired = self.fired + 1
        if self.drum[self.fired - 1] == 1:
            return "OH SHIIii.. you're dead, lol."
        return "Eh.. you survived."


class RouletteBotCommand(CommandsInterface):
    """This is the roulette bot command class"""

    def __init__(self, message_repository: MessageRepository):
        """Initializes the roulette bot command class"""
        self.message_repository = message_repository
        self.bullets = REVOLVER_BULLETS
        self.revolvers = {}

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roulette command"""
        return r"(\.[Rr]([Oo][Uu][Ll][Ee][Tt]{2}[Ee]|[Ee][Ll][Oo][Aa][Dd]|[Ee][Vv]\
        [Oo][Ll][Vv][Ee][Rr]\s[0-9]+)).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
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
            return revolver.reload(bullets)
        if re.fullmatch(
            re.compile(r"(\.[Rr][Ee][Vv][Oo][Ll][Vv][Ee][Rr]\s[0-9]+)"), message.text
        ):
            capacity = message.text[9:]
            capacity = capacity.replace(" ", "")
            capacity = safe_cast(capacity, int, REVOLVER_CHAMBERS)
            return revolver.set_capacity(capacity) + revolver.reload(self.bullets)
        return revolver.shoot()
