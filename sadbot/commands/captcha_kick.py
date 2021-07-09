"""Captcha kick bot command"""

from typing import Optional, List
import random

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_CALLBACK_QUERY
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_BAN_USER,
    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.classes.captcha import Captcha


class CaptchaKickBotCommand(CommandInterface):
    """This is the captcha bot command class"""

    def __init__(self, captcha: Captcha):
        """Initializes the captcha command"""
        self.captcha = captcha

    @property
    def handler_type(self) -> str:
        return BOT_HANDLER_TYPE_CALLBACK_QUERY

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching new users"""
        return r"captcha.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """'Welcomes' a new user"""
        callback_data = message.text.rsplit("-", 1)
        callback_data[0] = callback_data[0].split("-", 1)
        captcha_id = callback_data[0][1]
        captcha_sender_id = captcha_id.split(".")[1]
        if captcha_sender_id != str(message.sender_id):
            not_your_captcha_replies = [
                "That's not your captcha.",
                "Yoo tf you doing that ain't your business",
            ]
            not_yours = random.choice(not_your_captcha_replies)
            return [
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text=not_yours,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
            ]
        captcha_text = self.captcha.get_captcha_from_id(captcha_id)
        if captcha_text is None:
            print("Error: captcha not found in the database.")
            return None
        if callback_data[1] == captcha_text:
            correct_captcha_replies = ["Correct.", "Yo! You got it right!", "uwu nice"]
            correct_captcha = random.choice(correct_captcha_replies)
            welcome_replies = [
                f"Welcome @{message.sender_username}",
                f"!! Yooo welcome @{message.sender_username}",
                f"W-w-welcome @{message.sender_username} ~~",
            ]
            welcome_reply = random.choice(welcome_replies)
            self.captcha.delete_captcha(captcha_id)
            permissions = [
                {
                    "can_send_messages": True,
                    "can_send_media_messages": True,
                    "can_send_polls": True,
                    "can_send_other_messages": True,
                    "can_add_web_page_previews": True,
                    "can_change_info": True,
                    "can_invite_users": True,
                    "can_pin_messages": True,
                }
            ]
            return [
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text=correct_captcha,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                ),
                BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=welcome_reply),
                BotAction(
                    BOT_ACTION_TYPE_DELETE_MESSAGE,
                    reply_ban_user_id=message.sender_id,
                    reply_delete_message_id=message.reply_id,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                ),
                BotAction(
                    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
                    reply_permissions=permissions,
                    reply_ban_user_id=message.sender_id,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                ),
            ]
        return self.kick_user(message, captcha_id)

    def kick_user(self, message: Message, captcha_id: str, answer_callback_query: Optional[bool] = True) -> List[
        BotAction]:
        print("KICKING")
        print(message)
        new_user = message.sender_username
        kick_text = [
            "Begone bot",
            "lol i knew it was a bot",
            "There's space for only one bot here, and that's me",
            "Wrong captcha",
            "Oopsie-whooppsie owo s s s-owrry but the cawpthwa yowu enterwed was nwot corrwect ;-;",
        ]
        kick_text = random.choice(kick_text)
        kick_text += f"\n(I kicked @{new_user} (id {message.sender_id})"
        self.captcha.delete_captcha(captcha_id)
        replies = []
        if answer_callback_query:
            replies.append(
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text=kick_text,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                ),
            )
        replies += [
            BotAction(
                BOT_ACTION_TYPE_BAN_USER,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=kick_text,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_delete_message_id=message.reply_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
        return replies
