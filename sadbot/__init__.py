"""Bot initialization"""

import os
import sys

from sadbot.app import App
from sadbot.message import Message
from sadbot import config


__all__ = ["App", "Message", "run"]


def run() -> None:
    """Runs the bot"""
    token = os.getenv("TOKEN") or config.TOKEN
    if token == "" or token == "tokenplaceholder":
        sys.exit("You forgot to set the token")
    App(token)
