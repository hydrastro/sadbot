"""A sad telegram bot"""

import os
from sadbot import config
from sadbot import App


def run():
    """Runs the bot"""
    token = os.getenv("TOKEN") or config.TOKEN
    App(token)


if __name__ == "__main__":
    run()
