"""A sad telegram bot"""

import os
import config

from sadbot import App

if __name__ == "__main__":
    token = os.getenv("TOKEN") or config.token
    app = App(token)
