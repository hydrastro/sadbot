"""Captcha kick bot command"""

from typing import Optional, List
import random
import logging

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_CALLBACK_QUERY
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_BAN_USER,
    BOT_ACTION_TYPE_UNBAN_USER,
    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.classes.captcha import Captcha
from sadbot.chat_helper import ChatHelper


class CaptchaKickBotCommand(CommandInterface):
    """This is the captcha bot command class"""

    def __init__(self, captcha: Captcha, chat_helper: ChatHelper):
        """Initializes the captcha command"""
        self.captcha = captcha
        self.chat_helper = chat_helper

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
        self.captcha.delete_captcha(captcha_id)
        if captcha_text is None:
            logging.warning("Error: captcha not found in the database.")
            return None
        if callback_data[1] == captcha_text:
            correct_captcha_replies = ["Correct.", "Yo! You got it right!", "uwu nice"]
            correct_captcha = random.choice(correct_captcha_replies)
            new_user = (
                message.sender_name
                if message.sender_username is None
                else f"@{message.sender_username}"
            )
            welcome_replies = [
                f"Welcome {new_user}",
                f"!! Yooo welcome {new_user}",
                f"W-w-welcome {new_user} ~~",
            ]
            self.captcha.delete_captcha(captcha_id)
            welcome_reply = random.choice(welcome_replies)
            #permissions = self.chat_helper.get_user_permissions(message.chat_id, message.sender_id)
            #if permissions is None:
            permissions = self.chat_helper.get_chat_permissions(message.chat_id)
            if message.chat_id == -1_001_127_994_403:
                reply_image_file = open("./sadbot/data/grules.jpg", mode="rb")
                reply_image = reply_image_file.read()
                return [
                    BotAction(
                        BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                        reply_callback_query_id=message.message_id,
                        reply_text=correct_captcha,
                        reply_priority=BOT_ACTION_PRIORITY_HIGH,
                    ),
                    BotAction(
                        BOT_ACTION_TYPE_REPLY_IMAGE,
                        reply_text=welcome_reply,
                        reply_image=reply_image,
                    ),
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
        # return self.kick_user(message, captcha_id)
        return self.ask_user_to_join_again(message)

    def ask_user_to_join_again(self, message: Message) -> None:
        user = (
            message.sender_name
            if message.sender_username is None
            else f"@{message.sender_username}"
        )
        reply_text = f"{user} if you want to talk here you have to rejoin the chat and get a new captcha."
        wrong_captcha = "Wrong captcha"
        return [
            BotAction(
                BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                reply_callback_query_id=message.message_id,
                reply_text=wrong_captcha,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_ban_user_id=message.sender_id,
                reply_delete_message_id=message.reply_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]

    def kick_user(
        self,
        message: Message,
        captcha_id: str,
        answer_callback_query: Optional[bool] = True,
    ) -> List[BotAction]:
        new_user = (
            message.sender_name
            if message.sender_username is None
            else f"@{message.sender_username}"
        )
        kick_text = [
            "Begone bot",
            "lol i knew it was a bot",
            "There's space for only one bot here, and that's me",
            "Wrong captcha",
            "Oopsie-whooppsie *blushes* owo s s s-owrry but the cawpthwa yowu enterwed was nwot corrwect ;-; *starts twerking*",
            "Get rekt",
        ]
        kick_text = random.choice(kick_text)
        kick_text += f"\n(I kicked {new_user} (id {message.sender_id}))"
        self.captcha.delete_captcha(captcha_id)
        replies = []
        if answer_callback_query:
            replies.append(
                BotAction(
                    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
                    reply_callback_query_id=message.message_id,
                    reply_text=kick_text,
                    reply_priority=BOT_ACTION_PRIORITY_HIGH,
                )
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
            BotAction(
                BOT_ACTION_TYPE_UNBAN_USER,
                reply_ban_user_id=message.sender_id,
                reply_priority=BOT_ACTION_PRIORITY_HIGH,
            ),
        ]
        return replies
