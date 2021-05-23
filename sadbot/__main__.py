"""A sad telegram bot"""

import os
from sadbot import config
from sadbot.message_repository import MessageRepository
from sadbot import App

if __name__ == "__main__":
    token = os.getenv("TOKEN") or config.TOKEN
    message_repository = MessageRepository()
    app = App(message_repository, token)
