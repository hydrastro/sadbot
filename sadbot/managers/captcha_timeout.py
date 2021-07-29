"""Here is the captcha timeout manager"""
import datetime
from typing import Optional, List, Dict

from sadbot.message import Message
from sadbot.bot_action import BotAction
from sadbot.classes.captcha import Captcha
from sadbot.action_manager_interface import ActionManagerInterface
from sadbot.message_repository import MessageRepository
from sadbot.commands.captcha_kick import CaptchaKickBotCommand
from sadbot.chat_helper import ChatHelper


class CaptchaTimeoutManager(ActionManagerInterface):
    """Handles the captcha timeout"""

    def __init__(
        self,
        message_repository: MessageRepository,
        captcha: Captcha,
        chat_helper: ChatHelper,
    ):
        """Initializes the event handler"""
        self.message_repository = message_repository
        self.captcha = captcha
        self.start = datetime.datetime.utcnow().timestamp()
        self.captcha_kick = CaptchaKickBotCommand(self.captcha, chat_helper)

    def set_trigger_message(self, trigger_message: Message) -> None:
        """Sets the trigger message"""
        self.trigger_message = trigger_message

    def set_sent_message(self, sent_message: Message) -> None:
        """Sets the sent message"""
        self.sent_message = sent_message

    def set_callback_manager_info(self, callback_manager_info: Dict) -> None:
        """Sets the callback manager info"""
        if "captcha_id" in callback_manager_info:
            self.captcha_id = callback_manager_info["captcha_id"]
        if "captcha_expiration" in callback_manager_info:
            self.captcha_expiration = callback_manager_info["captcha_expiration"]

    @property
    def is_active(self) -> bool:
        """Returns the manager status"""
        return self.captcha.get_captcha_from_id(self.captcha_id) is not None

    def get_message(self) -> Message:
        return self.trigger_message

    def get_reply(self) -> Optional[List[BotAction]]:
        """Kicks the user who didn't complete the captcha"""
        self.trigger_message.reply_id = self.sent_message.message_id
        if self.captcha.get_captcha_from_id(self.captcha_id) is None:
            return None
        now = datetime.datetime.utcnow().timestamp()
        if self.captcha_expiration + self.start > now:
            return None
        return self.captcha_kick.kick_user(self.trigger_message, self.captcha_id, False)
