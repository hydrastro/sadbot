"""Captcha welcome bot command"""

from typing import Optional, List, Tuple
from io import BytesIO
from math import ceil
import random

from sadbot.command_interface import (
    CommandInterface,
    BOT_HANDLER_TYPE_NEW_USER,
)
from sadbot.message import Message
from sadbot.bot_reply import (
    BotAction,
    BOT_ACTION_TYPE_INLINE_KEYBOARD,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
)
from sadbot.classes.captcha import Captcha
from sadbot.config import CAPTCHA_KEYBOARD_BUTTONS_PER_LINE


class CaptchaWelcomeBotCommand(CommandInterface):
    """This is the captcha welcome bot command class, it 'welcomes' new users lol"""

    def __init__(self, captcha: Captcha):
        """Initializes the captcha command"""
        self.captcha = captcha

    @property
    def handler_type(self) -> str:
        return BOT_HANDLER_TYPE_NEW_USER

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching new users"""
        return r"test"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """'Welcomes' a new user"""
        if message.is_bot:
            return
        captcha_id = str(message.chat_id) + "." + str(message.sender_id)
        captcha_text, captcha_image = self.captcha.get_captcha(captcha_id)
        bytes_io = BytesIO()
        bytes_io.name = "captcha.jpeg"
        captcha_image.save(bytes_io, "JPEG")
        bytes_io.seek(0)
        new_user = message.sender_username
        welcome_message = [
            f"Welcome @{new_user}\nPlease solve the captcha.",
            f"W-w.. welcomee @{new_user} ~~ uwu~\nP-p pweaswe c-c.. *blushing* c- c-an ywou slwolve t-the capthwa for me {message.sender_name}-senpai~",
            f"Hmmmmm. I bet @{new_user} is a bot lol\nAnd you know..\nThere's space for only one bot here, and that's me.\nHere's your test.",
            f"Yoo @{new_user} wassup\nCan ya solve da captcha?",
            f"@{new_user} looking kinda sus, ngl.\nProve us ur not the impostor.",
        ]
        welcome_message = random.choice(welcome_message)
        callback_prefix = f"captcha-{captcha_id}-"
        keyboard_data = [
            {"text": captcha_text, "callback_data": callback_prefix + captcha_text}
        ]
        for i in range(0, 4):
            random_string = self.captcha.get_captcha_string()
            keyboard_data.append(
                {
                    "text": random_string,
                    "callback_data": f"{callback_prefix}{random_string}",
                }
            )
        random.shuffle(keyboard_data)
        keyboard_data = [keyboard_data]
        permissions = [
            {
                "can_send_messages": False,
                "can_send_media_messages": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
                "can_change_info": False,
                "can_invite_users": False,
                "can_pin_messages": False,
            }
        ]
        return [
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_permissions=permissions,
                reply_ban_user_id=message.sender_id,
            ),
            BotAction(
                BOT_ACTION_TYPE_INLINE_KEYBOARD,
                reply_text=welcome_message,
                reply_image=bytes_io,
                reply_inline_keyboard=keyboard_data,
            ),
        ]
