"""Roulette bot command"""

import random
import re

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.config import REVOLVER_CHAMBERS, REVOLVER_BULLETS


class Revolver:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.drum = [0] * self.capacity
        self.fired = 0

    def reload(self, bullets: int) -> str:
        if bullets > self.capacity:
            return "There are too many bullets lmao"
        for i in range(0, bullets):
            self.drum[i] = 1
        random.shuffle(self.drum)
        self.fired = 0
        return "Reloaded!"

    def shoot(self) -> str:
        if self.fired > self.capacity - 1:
            return "No more bullets, you have to .reload"
        self.fired = self.fired + 1
        if self.drum[self.fired - 1] == 1:
            return "OH SHIIii.. you're dead, lol."
        return "Eh.. you survived."


class RouletteBotCommand(CommandsInterface):
    """This is the roulette bot command class"""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository
        self.revolver = Revolver(REVOLVER_CHAMBERS)
        self.bullets = REVOLVER_BULLETS
        self.revolver.reload(self.bullets)

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the roulette command"""
        return r"(\.[Rr]([Oo][Uu][Ll][Ee][Tt]{2}[Ee]|[Ee][Ll][Oo][Aa][Dd])).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Plays the Russian roulette"""
        if re.fullmatch(re.compile(r"(\.[Rr][Ee][Ll][Oo][Aa][Dd]).*"), message.text):
            return self.revolver.reload(self.bullets)
        return self.revolver.shoot()
