""" This module contains the main app class and friends """

import datetime
import glob
import json
import re
import sqlite3
import time
from os.path import dirname, basename, isfile, join
from typing import Optional, Dict, List
import requests

from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.config import (
    MAX_REPLY_LENGTH,
    UPDATES_TIMEOUT,
    OUTGOING_REQUESTS_TIMEOUT,
    MESSAGES_CHAT_RATE_NUMBER,
    MESSAGES_CHAT_RATE_PERIOD,
    MESSAGES_USER_RATE_NUMBER,
    MESSAGES_USER_RATE_PERIOD,
)
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_REPLY_AUDIO,
    BOT_ACTION_TYPE_REPLY_FILE,
    BOT_ACTION_TYPE_REPLY_VOICE,
    BOT_ACTION_TYPE_BAN_USER,
    BOT_ACTION_TYPE_INLINE_KEYBOARD,
    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    # BOT_ACTION_PRIORITY_LOW,
    # BOT_ACTION_PRIORITY_MEDIUM,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.command_interface import (
    BOT_HANDLER_TYPE_NEW_USER,
    BOT_HANDLER_TYPE_CALLBACK_QUERY,
    BOT_HANDLER_TYPE_MESSAGE,
    # BOT_HANDLER_TYPE_EDITED_MESSAGE,
    # BOT_HANDLER_TYPE_PICTURE,
)


def snake_to_pascal_case(snake_str: str):
    """Converts a given snake_case string to PascalCase"""
    components = snake_str.split("_")
    return "".join(x.title() for x in components[0:])


def pascal_to_snake_case(pascal_str: str):
    """Converts a given PascalCase string to snake_case"""
    pascal_str = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", pascal_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", pascal_str).lower()


def is_bot_action_message(action_type: int) -> bool:
    """Checks if a bot outgoing action will result in/is a message"""
    return action_type in [
        BOT_ACTION_TYPE_REPLY_IMAGE,
        BOT_ACTION_TYPE_REPLY_AUDIO,
        BOT_ACTION_TYPE_REPLY_FILE,
        BOT_ACTION_TYPE_REPLY_TEXT,
        BOT_ACTION_TYPE_REPLY_VOICE,
        BOT_ACTION_TYPE_INLINE_KEYBOARD,
    ]


class App:
    """Main app class, starts the bot when it's called"""

    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.classes = {}
        con = sqlite3.connect("./messages.db")
        self.classes.update({"Connection": con})
        self.message_repository = MessageRepository(con)
        self.classes.update({"MessageRepository": self.message_repository})
        self.managers = {}
        self.commands = []
        self.load_commands()
        self.start_bot()

    def load_class(
        self, import_name: str, class_name: str, register_class: Optional[bool] = True
    ):
        """Dynamically loads and initializes a class given its name and its path"""
        arguments = []
        command_class = getattr(
            __import__(import_name, fromlist=[class_name]),
            class_name,
        )
        # todo: catch exceptions and return None
        if command_class.__init__.__class__.__name__ == "function":
            arguments_list = command_class.__init__.__annotations__
            for argument_name in arguments_list:
                dependency_class_name = arguments_list[argument_name].__name__
                if dependency_class_name in self.classes or self.load_class(
                    f"sadbot.classes.{pascal_to_snake_case(dependency_class_name)}",
                    dependency_class_name,
                ):
                    arguments.append(self.classes[dependency_class_name])
                else:
                    continue
        command_class = command_class(*arguments)
        if register_class:
            self.classes.update({class_name: command_class})
        return command_class

    def load_commands(self):
        """Loads the bot commands"""
        commands = glob.glob(join(dirname(__file__), "commands", "*.py"))
        for command_name in [basename(f)[:-3] for f in commands if isfile(f)]:
            if command_name == "__init__":
                continue
            class_name = snake_to_pascal_case(command_name) + "BotCommand"
            if not self.load_class(f"sadbot.commands.{command_name}", class_name):
                continue
            command_class = self.classes[class_name]
            self.commands.append(
                {"regex": command_class.command_regex, "class": command_class}
            )

    def dispatch_manager(
        self,
        class_name: str,
        trigger_message: Message,
        sent_message: Message,
        callback_manager_info: Optional[Dict],
    ) -> None:
        """Dispatches a new manager"""
        manager_filename = pascal_to_snake_case(class_name[:-7])
        manager = self.load_class(
            f"sadbot.managers.{manager_filename}", class_name, False
        )
        manager.set_trigger_message(trigger_message)
        manager.set_sent_message(sent_message)
        if callback_manager_info is not None:
            manager.set_callback_manager_info(callback_manager_info)
        class_id = len(self.managers)
        self.managers.update({class_id: manager})

    def get_managers_actions(self) -> Optional[List[List]]:
        """Returns the managers actions or kills them"""
        actions = []
        inactive_managers = []
        for manager in self.managers:
            if not self.managers[manager].is_active:
                inactive_managers.append(manager)
                continue
            temp = self.managers[manager].get_reply()
            if temp:
                actions.append([self.managers[manager].get_message(), temp])
        for manager in inactive_managers:
            del self.managers[manager]
        if not actions:
            return None
        return actions

    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict]:
        """Retrieves updates from the Telegram API"""
        url = f"{self.base_url}getUpdates?timeout={UPDATES_TIMEOUT}"
        if offset:
            url = f"{url}&offset={offset + 1}"
        req = requests.get(url)
        if not req.ok:
            print(f"Failed to retrieve updates from server - details: {req.json()}")
            return None

        return json.loads(req.content)

    def send_message_and_update_db(
        self, message: Message, reply_info: BotAction
    ) -> Optional[List]:
        """Sends a messages and updates the database if it's successfully sent"""
        user_trigger_time = self.message_repository.get_n_timestamp_user(
            message.sender_id, MESSAGES_USER_RATE_NUMBER
        )
        chat_trigger_time = self.message_repository.get_n_timestamp_chat(
            message.chat_id, MESSAGES_CHAT_RATE_NUMBER
        )
        self.message_repository.log_bot_trigger(message.chat_id, message.sender_id)
        now = datetime.datetime.utcnow().timestamp()
        if reply_info.reply_priority != BOT_ACTION_PRIORITY_HIGH:
            if user_trigger_time > now - MESSAGES_USER_RATE_PERIOD:
                print(
                    f"Message not sent: user trigger limit exceeded - details:"
                    f"user id={message.sender_id} user last trigger time={user_trigger_time}"
                )
                return None
            if chat_trigger_time > now - MESSAGES_CHAT_RATE_PERIOD:
                print(
                    f"Message not sent: chat trigger limit exceeded - details:"
                    f" chat id={message.chat_id} chat last trigger time={chat_trigger_time}"
                )
                return None
        sent_message = self.send_message(message.chat_id, reply_info)
        if sent_message is None:
            return None
        # this needs to be done better, along with the storage for non-text messages
        if sent_message.get("result") and is_bot_action_message(reply_info.reply_type):
            result = sent_message.get("result")
            username = (
                None if "username" not in result["from"] else result["from"]["username"]
            )
            sent_message_dataclass = Message(
                result["message_id"],
                result["from"]["first_name"],
                result["from"]["id"],
                message.chat_id,
                reply_info.reply_text,
                None,
                username,
                True,
            )
            self.message_repository.insert_message(sent_message_dataclass)
            if reply_info.reply_callback_manager_name is not None:
                self.dispatch_manager(
                    reply_info.reply_callback_manager_name,
                    message,
                    sent_message_dataclass,
                    reply_info.reply_callback_manager_info,
                )
        return sent_message

    def send_message(self, chat_id: int, reply: BotAction) -> Optional[List]:
        """Sends a message"""
        data = {"chat_id": chat_id}
        files = None
        reply_text = reply.reply_text
        if reply.reply_type == BOT_ACTION_TYPE_REPLY_TEXT:
            api_method = "sendMessage"
            if not reply.reply_text:
                return None
            if len(reply_text) > MAX_REPLY_LENGTH:
                reply_text = reply_text[:MAX_REPLY_LENGTH] + "..."
            data.update({"text": reply_text})
            parsemode = reply.reply_text_parsemode
            if parsemode is not None:
                data.update({"parsemode": parsemode})
        elif reply.reply_type == BOT_ACTION_TYPE_REPLY_IMAGE:
            api_method = "sendPhoto"
            files = {"photo": reply.reply_image}
            data.update({"caption": reply_text})
        elif reply.reply_type == BOT_ACTION_TYPE_REPLY_AUDIO:
            api_method = "sendAudio"
            files = {"audio": reply.reply_audio}
        elif reply.reply_type == BOT_ACTION_TYPE_REPLY_FILE:
            api_method = "sendDocument"
            files = {"file": reply.reply_file}
        elif reply.reply_type == BOT_ACTION_TYPE_REPLY_VOICE:
            api_method = "sendVoice"
            files = {"voice": reply.reply_voice}
        elif reply.reply_type == BOT_ACTION_TYPE_BAN_USER:
            api_method = "banChatMember"
            data.update(
                {
                    "chat_id": chat_id,
                    "user_id": reply.reply_ban_user_id,
                }
            )
        elif reply.reply_type == BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER:
            api_method = "restrictChatMember"
            data.update(
                {
                    "chat_id": chat_id,
                    "user_id": reply.reply_ban_user_id,
                    "permissions": json.dumps(reply.reply_permissions[0]),
                    "until_date": reply.reply_restrict_until_date,
                }
            )
        elif reply.reply_type == BOT_ACTION_TYPE_INLINE_KEYBOARD:
            # here we need to check reply_type
            api_method = "sendPhoto"
            files = {"photo": reply.reply_image}
            data.update({"caption": reply_text})
            data.update(
                {
                    "reply_markup": json.dumps(
                        {"inline_keyboard": reply.reply_inline_keyboard}
                    )
                }
            )
        elif reply.reply_type == BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY:
            api_method = "answerCallbackQuery"
            data.update(
                {
                    "callback_query_id": reply.reply_callback_query_id,
                    "text": reply.reply_text,
                }
            )
        elif reply.reply_type == BOT_ACTION_TYPE_DELETE_MESSAGE:
            api_method = "deleteMessage"
            data.update(
                {"chat_id": chat_id, "message_id": reply.reply_delete_message_id}
            )
        else:
            return None
        # headers={"Content-Type": "application/json"},
        req = requests.post(
            f"{self.base_url}{api_method}",
            data=data,
            files=files,
            timeout=OUTGOING_REQUESTS_TIMEOUT,
        )
        if not req.ok:
            print(f"Failed sending message - details: {req.json()}")
            return None
        return json.loads(req.content)

    def get_replies(self, message: Message) -> Optional[list]:
        """Checks if a bot command is triggered and gets its reply"""
        text = message.text
        if not text:
            return None
        messages = []
        for command in self.commands:
            if command["class"].handler_type == BOT_HANDLER_TYPE_MESSAGE:
                try:
                    if re.fullmatch(re.compile(command["regex"]), text):
                        reply_message = command["class"].get_reply(message)
                        if reply_message is None:
                            continue
                        messages += reply_message
                except re.error:
                    return None
        return messages

    def handle_messages(self, message: Message) -> None:
        """Handles the messages"""
        replies_info = self.get_replies(message)
        if replies_info is None:
            return
        for reply_info in replies_info:
            self.send_message_and_update_db(message, reply_info)

    def handle_new_chat_members(self, message: Message) -> None:
        """Handles new chat members events"""
        for command in self.commands:
            if command["class"].handler_type == BOT_HANDLER_TYPE_NEW_USER:
                reply_message = command["class"].get_reply(message)
                if reply_message is None:
                    continue
                for reply in reply_message:
                    self.send_message_and_update_db(message, reply)

    def handle_photos(self, message: Message) -> None:
        """Handles photo messages"""
        return self.handle_messages(message)

    def handle_callback_query(self, message: Message) -> None:
        """Handles inline keyboard inputs"""
        for command in self.commands:
            if command["class"].handler_type == BOT_HANDLER_TYPE_CALLBACK_QUERY:
                try:
                    if re.fullmatch(re.compile(command["regex"]), message.text):
                        reply_message = command["class"].get_reply(message)
                        if reply_message is None:
                            continue
                        for reply in reply_message:
                            self.send_message_and_update_db(message, reply)
                except re.error:
                    return None
        return None

    def handle_managers(self) -> None:
        """Handles the bot managers"""
        actions = self.get_managers_actions()
        if actions is None:
            return
        for manager_message in actions:
            for bot_action in manager_message[1]:
                self.send_message_and_update_db(manager_message[0], bot_action)

    def start_bot(self) -> None:
        """Starts the bot"""
        update_id = None
        while True:
            self.handle_managers()
            updates = self.get_updates(offset=update_id) or {}
            for item in updates.get("result", []):
                update_id = item["update_id"]
                # catching the text messages
                if "message" in item:
                    username = (
                        None
                        if "username" not in item["message"]["from"]
                        else item["message"]["from"]["username"]
                    )
                    message = Message(
                        item["message"]["message_id"],
                        item["message"]["from"]["first_name"],
                        item["message"]["from"]["id"],
                        item["message"]["chat"]["id"],
                        None,
                        item["message"].get("reply_to_message", {}).get("message_id"),
                        username,
                    )
                    if "text" in item["message"]:
                        message.text = str(item["message"]["text"])
                        self.handle_messages(message)
                    if "photo" in item["message"]:
                        if "caption" in item["message"]:
                            message.text = str(item["message"]["caption"])
                        self.handle_photos(message)
                    if "new_chat_member" in item["message"]:
                        message.sender_id = item["message"]["new_chat_member"]["id"]
                        message.sender_username = (
                            None
                            if "username" not in item["message"]["new_chat_member"]
                            else item["message"]["new_chat_member"]["username"]
                        )
                        message.sender_name = item["message"]["new_chat_member"][
                            "first_name"
                        ]
                        message.is_bot = item["message"]["new_chat_member"]["is_bot"]
                        self.handle_new_chat_members(message)
                    self.message_repository.insert_message(message)
                if "edited_message" in item:
                    if "text" in item["edited_message"]:
                        text = item["edited_message"]["text"]
                        message_id = item["edited_message"]["message_id"]
                        self.message_repository.edit_message(message_id, text)
                if "callback_query" in item:
                    username = (
                        None
                        if "username" not in item["callback_query"]["from"]
                        else item["callback_query"]["from"]["username"]
                    )
                    message = Message(
                        item["callback_query"]["id"],
                        item["callback_query"]["from"]["first_name"],
                        item["callback_query"]["from"]["id"],
                        item["callback_query"]["message"]["chat"]["id"],
                        item["callback_query"]["data"],
                        item["callback_query"]["message"]["message_id"],
                        username,
                    )
                    self.handle_callback_query(message)
            time.sleep(1)
