"""Captcha kick bot command"""

from typing import Optional, List, Tuple
from io import BytesIO
import random

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_KEYBOARD_INPUT
from sadbot.message import Message
from sadbot.bot_reply import BotAction, BOT_ACTION_TYPE_KICK_USER
from sadbot.classes.captcha import Captcha


class CaptchaKickBotCommand(CommandInterface):
    """This is the captcha bot command class"""

    def __init__(self, captcha: Captcha):
        """Initializes the captcha command"""
        self.captcha = captcha

    @property
    def handler_type(self) -> str:
        return BOT_HANDLER_TYPE_KEYBOARD_INPUT

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching new users"""
        return r"test"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """'Welcomes' a new user"""
        captcha_id = str(message.chat_id) + "." + str(message.sender_id)
        captcha_text = ""
        if self.captcha.verify_captcha(captcha_id, captcha_text):
            return
        new_user = message.sender_username
        kick_text = [f"Welcome @{new_user}\nPlease solve the captcha.",
                           f"W-w.. welcomee @{new_user} ~~ uwu~\nP-p pweaswe can ywou slwolve t-the capthwa for me {message.sender_name}-senpai~",
                           f"Hmmmmm. I bet @{new_user} is a bot lol\nAnd you know..\nThere's space for only one bot here, and that's me.\nHere's your test.",
                           f"Yoo @{new_user} wassup\nCan ya solve da captcha?"]
        kick_text = random.choice(kick_text)
        return [
            BotAction(BOT_ACTION_TYPE_KICK_USER, reply_text=kick_text, reply_kick_user_id=message.sender_id)
        ]
