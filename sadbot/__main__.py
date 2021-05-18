"""A sad telegram bot"""

import os
from sadbot import config

from sadbot import App

if __name__ == "__main__":
    token = os.getenv("TOKEN") or config.TOKEN
    app = App(token)
