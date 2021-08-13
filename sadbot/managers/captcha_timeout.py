"""Here is the captcha timeout manager"""
import datetime
from typing import Optional, List, Dict

from sadbot.app import App
from sadbot.message import Message
from sadbot.classes.captcha import Captcha
from sadbot.action_manager_interface import ActionManagerInterface
from sadbot.message_repository import MessageRepository
from sadbot.commands.captcha_kick import CaptchaKickBotCommand
from sadbot.classes.permissions import Permissions


class CaptchaTimeoutManager(ActionManagerInterface):
    """Handles the captcha timeout"""

    def __init__(
        self,
        app: App,
        message_repository: MessageRepository,
        captcha: Captcha,
        permissions: Permissions,
    ):
        """Initializes the event handler"""
        self.message_repository = message_repository
        self.captcha = captcha
        self.captcha_kick = CaptchaKickBotCommand(app, captcha, permissions)
        self.instances: Dict[str, Dict] = {}
        self.restore_dead_instances()

    def restore_dead_instances(self) -> None:
        """Restores dead submanager instances in case the bot have restarted."""
        unsolved_captchas = self.captcha.get_unsolved_captchas()
        if unsolved_captchas is None:
            return
        for captcha in unsolved_captchas:
            captcha_id = captcha[0]
            (
                _chat_id,
                _sender_id,
                message_id,
                _start_time,
                _expiration,
            ) = captcha_id.split(".")
            trigger_message = self.message_repository.get_message_from_id(message_id)
            self.instances[captcha_id] = {
                "trigger_message": trigger_message,
                "sent_message": None,
                "captcha_id": captcha_id,
            }

    def handle_callback(
        self,
        trigger_message: Message,
        sent_message: Optional[Message],
        callback_manager_info: Optional[Dict],
    ) -> None:
        if callback_manager_info is None:
            return
        instance_id = callback_manager_info["captcha_id"]
        self.instances[instance_id] = {
            "trigger_message": trigger_message,
            "sent_message": sent_message,
            "captcha_id": instance_id,
        }

    def get_actions(self) -> Optional[List[List]]:
        """Kicks the user who didn't complete the captcha"""
        actions = []
        inactive_instance_ids = []
        now = datetime.datetime.utcnow().timestamp()
        for captcha_id in self.instances:
            if self.captcha.get_captcha_from_id(captcha_id) is None:
                inactive_instance_ids.append(captcha_id)
                continue
            (
                _chat_id,
                _sender_id,
                _message_id,
                start_time,
                expiration,
            ) = captcha_id.split(".")
            if int(expiration) + int(start_time) > now:
                continue
            trigger_message = self.instances[captcha_id]["trigger_message"]
            sent_message = self.instances[captcha_id]["sent_message"]
            message_to_delete = None
            if sent_message is not None:
                message_to_delete = sent_message.message_id
            actions.append(
                [
                    trigger_message,
                    self.captcha_kick.kick_user(
                        trigger_message, captcha_id, False, message_to_delete
                    ),
                ]
            )
        for captcha_id in inactive_instance_ids:
            del self.instances[captcha_id]
        return actions
