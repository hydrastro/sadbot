"""A sad telegram bot"""

import os
from sadbot import config
from sadbot import App

def run():
    token = os.getenv("TOKEN") or config.TOKEN
    app = App(token)

if __name__ == "__main__":
    run()
