"""Here is the captcha timeout manager"""
import datetime
from typing import Optional, List

from sadbot.message import Message
from sadbot.bot_action import BotAction
from sadbot.classes.captcha import Captcha
from sadbot.action_manager_interface import ActionManagerInterface
from sadbot.message_repository import MessageRepository
from sadbot.commands.captcha_kick import CaptchaKickBotCommand


class CaptchaTimeoutManager(ActionManagerInterface):
    """Handles the captcha timeout"""

    def __init__(self, message_repository: MessageRepository, captcha: Captcha, captcha_id: str, timeout: int):
        """Initializes the event handler"""
        self.message_repository = MessageRepository
        self.captcha = captcha
        self.captcha_id = captcha_id
        self.timeout = timeout
        self.start = datetime.datetime.utcnow().timestamp()
        self.captcha_kick = CaptchaKickBotCommand(self.captcha)
        message = message_repository.get_message_from_reply_info_id(captcha_id)
        print(message)
        self.kick_id = message_repository.get_reply_info_data(captcha_id)
        message.sender_id = self.kick_id
        self.message = message

    @property
    def is_active(self) -> bool:
        """Returns the handler status"""
        print("CHECKING IF ACTIVE")
        print(self.captcha.get_captcha_from_id(self.captcha_id))
        return self.captcha.get_captcha_from_id(self.captcha_id) is not None

    def get_message(self) -> Message:
        print("message")
        print(self.message)
        return self.message

    def get_reply(self) -> Optional[List[BotAction]]:
        """Kicks the user who didn't complete the captcha"""
        if self.captcha.get_captcha_from_id(self.captcha_id) is None:
            return None
        now = datetime.datetime.utcnow().timestamp()
        if self.timeout + self.start > now:
            return None
        return self.captcha_kick.kick_user(self.message, self.captcha_id, False)
