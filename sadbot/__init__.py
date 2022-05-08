"""Bot initialization"""

import os
import sys
import signal

from sadbot.app import App
from sadbot.message import Message
from sadbot import config


__all__ = ["App", "Message", "run"]


def run() -> None:
    """Runs the bot"""
    token = os.getenv("TOKEN") or config.TOKEN
    if token in ("", "tokenplaceholder"):
        sys.exit("You forgot to set the token")

    def handler(signum, _):
        msg = f"Closing the bot, because signal {signum} was received"
        print(msg)
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    App(token)
