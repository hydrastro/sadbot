"""Bot initialization"""

import os

from sadbot.app import App
from sadbot.message import Message
from sadbot import config


__all__ = ["App", "Message", "run"]


def run() -> None:
    """Runs the bot"""
    token = os.getenv("TOKEN") or config.TOKEN
    App(token)
