"""Captcha welcome bot command"""

from typing import Optional, List
from io import BytesIO
from math import ceil
import random
import datetime

from sadbot.app import App, CHAT_MEMBER_STATUS_RESTRICTED
from sadbot.classes.permissions import Permissions
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_NEW_USER
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.classes.captcha import Captcha
from sadbot.config import (
    CAPTCHA_KEYBOARD_BUTTONS_PER_LINE,
    CAPTCHA_EXTRA_TEXTS_NUMBER,
    CAPTCHA_EXPIRATION,
)
from sadbot.message_repository import MessageRepository
from sadbot.chat_permissions import ChatPermissions
from sadbot.functions import convert_time


class CaptchaWelcomeBotCommand(CommandInterface):
    """This is the captcha welcome bot command class, it 'welcomes' new users lol"""

    def __init__(
        self,
        app: App,
        permissions: Permissions,
        captcha: Captcha,
        message_repository: MessageRepository,
    ):
        """Initializes the captcha command"""
        self.app = app
        self.permissions = permissions
        self.captcha = captcha
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        return BOT_HANDLER_TYPE_NEW_USER

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching new users"""
        return r"test"

    def get_keyboard(self, captcha_id: str, captcha_text: str) -> List:
        """Returns the inline keyboard for the captcha"""
        callback_prefix = f"captcha-{captcha_id}-"
        keyboard_data = [
            {"text": captcha_text, "callback_data": callback_prefix + captcha_text}
        ]
        for i in range(0, CAPTCHA_EXTRA_TEXTS_NUMBER):
            random_string = self.captcha.get_captcha_string()
            keyboard_data.append(
                {
                    "text": random_string,
                    "callback_data": f"{callback_prefix}{random_string}",
                }
            )
        random.shuffle(keyboard_data)
        inline_keyboard = []
        for i in range(
            0,
            ceil((CAPTCHA_EXTRA_TEXTS_NUMBER + 1) / CAPTCHA_KEYBOARD_BUTTONS_PER_LINE),
        ):
            temp_list = []
            for j in range(
                i * CAPTCHA_KEYBOARD_BUTTONS_PER_LINE,
                i * CAPTCHA_KEYBOARD_BUTTONS_PER_LINE
                + CAPTCHA_KEYBOARD_BUTTONS_PER_LINE,
            ):
                if j > CAPTCHA_EXTRA_TEXTS_NUMBER:
                    continue
                temp_list.append(keyboard_data[j])
            inline_keyboard.append(temp_list)
        return inline_keyboard

    @staticmethod
    def get_welcome_message(new_user: str) -> str:
        """Returns a 'welcome' message lol"""
        time_string = convert_time(CAPTCHA_EXPIRATION)
        welcome_message_replies = [
            f"Welcome {new_user}\nPlease solve the captcha.",
            f"""W-w.. welcomee {new_user} ~~ uwu~\nP-p pweaswe c-c.. *blushing* c- c-an """
            + """ywou slwolve t-the capthwa for me {new_user} -senpai ~~""",
            f"""Hmmmmm. I bet {new_user} is a bot lol\nAnd you know..\nThere's space for """
            + """one bot here, and that's me.\nHere's your test.""",
            f"Yoo {new_user} wassup\nCan ya solve da captcha?",
            f"{new_user} looking kinda sus, ngl.\nProve us ur not the impostor.",
            f"""嗨 {new_user}，歡迎加入群。 請填寫驗證碼以驗證您是人類。 {time_string}"""
            + """內不輸入驗證碼，會被自動踢出群。 在此之前，您將無法發送消息。 """
            + """這個組裡只有一個機器人，那個機器人就是我。""",
        ]
        return random.choice(welcome_message_replies)

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns a reply that 'welcomes' a new user"""
        if message is None:
            return None
        if message.is_bot:
            return None
        expiration = CAPTCHA_EXPIRATION
        captcha_id = (
            str(message.chat_id)
            + "."
            + str(message.sender_id)
            + "."
            + str(message.message_id)
            + "."
            + str(int(datetime.datetime.utcnow().timestamp()))
            + "."
            + str(expiration)
        )
        captcha_text, captcha_image = self.captcha.get_captcha(captcha_id)
        bytes_io = BytesIO()
        bytes_io.name = "captcha.jpeg"
        captcha_image.save(bytes_io, "JPEG")
        bytes_io.seek(0)
        image_bytes = bytes_io.read()
        new_user = message.sender_name
        if message.sender_username is not None:
            new_user = "@" + message.sender_username
        welcome_message = self.get_welcome_message(new_user)
        inline_keyboard = self.get_keyboard(captcha_id, captcha_text)
        permissions = ChatPermissions(
            False, False, False, False, False, False, False, False
        )
        user_status_and_permissions = self.app.get_user_status_and_permissions(
            message.chat_id, message.sender_id
        )
        if (
            user_status_and_permissions is not None
            and user_status_and_permissions[0] == CHAT_MEMBER_STATUS_RESTRICTED
        ):
            self.permissions.set_user_permissions(
                message.sender_id, message.chat_id, user_status_and_permissions[1]
            )
        callback_manager_name = "CaptchaTimeoutManager"
        callback_manager_info = {"captcha_id": captcha_id}
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_IMAGE,
                reply_text=welcome_message,
                reply_image=image_bytes,
                reply_inline_keyboard=inline_keyboard,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
                reply_callback_manager_name=callback_manager_name,
                reply_callback_manager_info=callback_manager_info,
            ),
            BotAction(
                BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                reply_permissions=permissions,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
