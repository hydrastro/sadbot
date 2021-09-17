"""This module contains the main app class and friends"""

import datetime
import glob
import json
import threading
import re
import sqlite3
import time
from os.path import dirname, basename, isfile, join
from typing import Optional, Dict, List, Any
import logging
from dataclasses import asdict
import requests

from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.config import (
    OFFLINE_ANTIFLOOD_TIMEOUT,
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
    BOT_ACTION_TYPE_REPLY_VIDEO,
    BOT_ACTION_TYPE_REPLY_AUDIO,
    BOT_ACTION_TYPE_REPLY_FILE,
    BOT_ACTION_TYPE_REPLY_VOICE,
    BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
    BOT_ACTION_TYPE_BAN_USER,
    BOT_ACTION_TYPE_INLINE_KEYBOARD,
    BOT_ACTION_TYPE_ANSWER_CALLBACK_QUERY,
    BOT_ACTION_TYPE_DELETE_MESSAGE,
    BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER,
    BOT_ACTION_TYPE_UNBAN_USER,
    BOT_ACTION_TYPE_PROMOTE_CHAT_MEMBER,
    BOT_ACTION_TYPE_NONE,
    # BOT_ACTION_PRIORITY_LOW,
    # BOT_ACTION_PRIORITY_MEDIUM,
    BOT_ACTION_PRIORITY_HIGH,
)
from sadbot.command_interface import (
    BOT_HANDLER_TYPE_NEW_USER,
    BOT_HANDLER_TYPE_CALLBACK_QUERY,
    # BOT_HANDLER_TYPE_EDITED_MESSAGE,
    # BOT_HANDLER_TYPE_PICTURE,
    BOT_HANDLER_TYPE_MESSAGE,
)
from sadbot.chat_permissions import ChatPermissions


CHAT_MEMBER_STATUS_CREATOR = 0
CHAT_MEMBER_STATUS_ADMIN = 1
CHAT_MEMBER_STATUS_USER = 2  # member
CHAT_MEMBER_STATUS_LEFT = 3
CHAT_MEMBER_STATUS_BANNED = 4  # kicked
CHAT_MEMBER_STATUS_RESTRICTED = 5


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
        BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
        BOT_ACTION_TYPE_INLINE_KEYBOARD,
    ]


class App:
    """Main app class, starts the bot when it's called"""

    def __init__(self, token: str) -> None:
        logging.basicConfig(filename="sadbot.log", level=logging.INFO)
        logging.info("Started sadbot")
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.update_id = None
        self.classes: Dict[str, object] = {"App": self}
        con = sqlite3.connect("./messages.db", check_same_thread=False)
        self.classes["Connection"] = con
        self.message_repository = MessageRepository(con)
        self.classes["MessageRepository"] = self.message_repository
        self.managers: Dict[str, object] = {}
        self.commands: List[Dict] = []
        self.load_commands()
        self.load_managers()
        self.start_bot()

    def load_class(
        self, import_name: str, class_name: str, register_class: Optional[bool] = True
    ) -> object:
        """Dynamically loads and initializes a class given its name and its path"""
        arguments = []
        command_class = getattr(
            __import__(import_name, fromlist=[class_name]), class_name
        )
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

    def load_commands(self) -> None:
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
                {
                    "regex": getattr(command_class, "command_regex"),
                    "class": command_class,
                }
            )

    def load_managers(self) -> None:
        """Loads the bot managers"""
        managers = glob.glob(join(dirname(__file__), "managers", "*.py"))
        for manager_name in [basename(f)[:-3] for f in managers if isfile(f)]:
            if manager_name == "__init__":
                continue
            class_name = snake_to_pascal_case(manager_name) + "Manager"
            if not self.load_class(f"sadbot.managers.{manager_name}", class_name):
                continue
            manager_class = self.classes[class_name]
            self.managers[class_name] = manager_class

    def get_chat_permissions_api_json(
        self, chat_id: int, user_id: int = None
    ) -> Optional[Dict]:
        """Returns the json list of a chat or a user's permissions"""
        data = {"chat_id": chat_id}
        api_method = "getChat"
        if user_id is not None:
            api_method = "getChatMember"
            data.update({"user_id": user_id})
        try:
            req = requests.post(
                f"{self.base_url}{api_method}",
                data=data,
                timeout=OUTGOING_REQUESTS_TIMEOUT,
            )
        except requests.exceptions.RequestException:
            logging.error("An error occured sending the getChatMember request")
            return None
        if not req.ok:
            logging.error("Failed sending message - details: %s", req.json())
            return None
        return json.loads(req.content)

    def get_user_status_and_permissions(  # pylint: disable=too-many-return-statements
        self, chat_id: int, user_id: int
    ) -> Optional[List]:
        """Returns a list containing the user status and its permissions if there is any"""
        data = self.get_chat_permissions_api_json(chat_id, user_id)
        if data is None or "result" not in data:
            return None
        data = data["result"]
        if data is None or "status" not in data:
            return None
        status = data["status"]
        if status == "creator":
            return [CHAT_MEMBER_STATUS_CREATOR]
        if status == "left":
            return [CHAT_MEMBER_STATUS_LEFT]
        if status == "member":
            return [CHAT_MEMBER_STATUS_USER, self.get_chat_permissions(chat_id)]
        if status == "kicked":
            permissions = ChatPermissions(ban_until_date=data.get("until_date", 0))
            return [CHAT_MEMBER_STATUS_BANNED, permissions]
        permissions = ChatPermissions(
            can_change_info=data.get("can_change_info", False),
            can_invite_users=data.get("can_invite_users", False),
            can_pin_messages=data.get("can_pin_messages", False),
            can_be_edited=data.get("can_be_edited", False),
            can_manage_chat=data.get("can_manage_chat", False),
            can_delete_messages=data.get("can_delete_messages", False),
            can_restrict_members=data.get("can_restrict_members", False),
            can_promote_members=data.get("can_promote_members", False),
            can_manage_voice_chats=data.get("can_manage_voice_chats", False),
            can_post_messages=data.get("can_post_messages", False),
            can_edit_messages=data.get("can_edit_messages", False),
            can_send_messages=data.get("can_send_messages", False),
            can_send_media_messages=data.get("can_send_media_messages", False),
            can_send_polls=data.get("can_send_pools", False),
            can_send_other_messages=data.get("can_send_other_messages", False),
            can_add_web_page_previews=data.get("can_add_webpage_previews", False),
        )
        if status == "administrator":
            return [CHAT_MEMBER_STATUS_ADMIN, permissions]
        return [CHAT_MEMBER_STATUS_RESTRICTED, permissions]

    def get_chat_permissions(self, chat_id: int) -> Optional[ChatPermissions]:
        """Returns the default chat permissions"""
        data = self.get_chat_permissions_api_json(chat_id)
        if data is None:
            return None
        if "result" not in data or "permissions" not in data["result"]:
            return None
        permissions = data["result"]["permissions"]
        return ChatPermissions(
            can_send_messages=permissions.get("can_send_messages", False),
            can_send_media_messages=permissions.get("can_send_media_messages", False),
            can_send_polls=permissions.get("can_send_polls", False),
            can_send_other_messages=permissions.get("can_send_other_messages", False),
            can_add_web_page_previews=permissions.get(
                "can_add_web_page_previews", False
            ),
            can_change_info=permissions.get("can_change_info", False),
            can_invite_users=permissions.get("can_invite_users", False),
            can_pin_messages=permissions.get("can_pin_messages", False),
        )

    def dispatch_manager(
        self,
        class_name: str,
        trigger_message: Message,
        sent_message: Message,
        callback_manager_info: Optional[Dict],
    ) -> None:
        """Dispatches a new manager"""
        getattr(self.managers[class_name], "handle_callback")(
            trigger_message, sent_message, callback_manager_info
        )

    def get_managers_actions(self) -> Optional[List[List]]:
        """Returns the managers actions"""
        actions = []
        for manager in self.managers.items():
            temp = getattr(manager[1], "get_actions")()
            if temp:
                actions.append(temp)
        if not actions:
            return None
        return actions

    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict]:
        """Retrieves updates from the Telegram API"""
        url = f"{self.base_url}getUpdates?timeout={UPDATES_TIMEOUT}"
        if offset:
            url = f"{url}&offset={offset + 1}"
        try:
            req = requests.get(url, timeout=UPDATES_TIMEOUT)
        except requests.exceptions.RequestException:
            logging.error("An error occurred sending the getUpdates request")
            return None
        if not req.ok:
            logging.error(
                "Failed to retrieve updates from server - details: %s", req.json()
            )
            return None
        return json.loads(req.content)

    def send_message_and_update_db(
        self, message: Message, reply_info: BotAction
    ) -> Optional[Dict]:
        """Sends a messages and updates the database if it's successfully sent"""
        if (
            message.message_time is not None
            and message.message_time != 0
            and time.time() - message.message_time > OFFLINE_ANTIFLOOD_TIMEOUT
        ):
            logging.warning("Dropping message: I am too late")
            return None
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
                logging.error(
                    "Message not sent: user trigger limit exceeded - details: "
                    "user id=%s user last trigger time=%s",
                    message.sender_id,
                    user_trigger_time,
                )
                return None
            if chat_trigger_time > now - MESSAGES_CHAT_RATE_PERIOD:
                logging.warning(
                    "Message not sent: chat trigger limit exceeded - details: "
                    "chat id=%s chat last trigger time=%s",
                    message.chat_id,
                    chat_trigger_time,
                )
                return None
        chat_id = (
            message.chat_id
            if reply_info.reply_chat_id is None
            else reply_info.reply_chat_id
        )
        sent_message = self.send_message(chat_id, reply_info)
        if sent_message is None:
            return None
        # this needs to be done better, along with the storage for non-text messages
        if sent_message.get("result") and is_bot_action_message(reply_info.reply_type):
            result = sent_message.get("result", {})
            sent_message_dataclass = Message(
                result["message_id"],
                result["from"]["first_name"],
                result["from"]["id"],
                message.chat_id,
                reply_info.reply_text,
                None,
                result["from"].get("username", None),
                True,
                result["date"],
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

    def send_message(  # pylint: disable=too-many-branches, too-many-statements too-many-return-statements
        self, chat_id: int, reply: BotAction
    ) -> Optional[Dict]:
        """Sends a message"""
        logging.info("Sending message")
        data: Dict[str, Any] = {"chat_id": chat_id}
        files = None
        reply_text = reply.reply_text
        if reply.reply_type == BOT_ACTION_TYPE_NONE:
            return None
        if reply.reply_type == BOT_ACTION_TYPE_REPLY_TEXT:
            api_method = "sendMessage"
            if reply_text is None:
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
        elif reply.reply_type == BOT_ACTION_TYPE_REPLY_VIDEO:
            api_method = "sendVideo"
            files = {"video": reply.reply_video}
            data.update({"caption": reply_text})
        elif reply.reply_type == BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE:
            api_method = "sendVideo"
            data.update({"video": reply.reply_online_media_url, "caption": reply_text})
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
            data.update({"chat_id": chat_id, "user_id": reply.reply_ban_user_id})
        elif reply.reply_type == BOT_ACTION_TYPE_UNBAN_USER:
            api_method = "unbanChatMember"
            data.update({"chat_id": chat_id, "user_id": reply.reply_ban_user_id})
        elif reply.reply_type == BOT_ACTION_TYPE_RESTRICT_CHAT_MEMBER:
            api_method = "restrictChatMember"
            permissions = json.dumps(asdict(reply.reply_permissions))
            data.update(
                {
                    "chat_id": chat_id,
                    "user_id": reply.reply_ban_user_id,
                    "permissions": permissions,
                }
            )
            if reply.reply_restrict_until_date is not None:
                data.update({"until_date": reply.reply_restrict_until_date})
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
        elif reply.reply_type == BOT_ACTION_TYPE_PROMOTE_CHAT_MEMBER:
            api_method = "promoteChatMember"
            permissions_class = reply.reply_permissions
            if permissions_class is None:
                permissions_class = self.get_chat_permissions(chat_id)
            if permissions_class is None:
                return None
            data.update({"chat_id": chat_id, "user_id": reply.reply_ban_user_id})
            if permissions_class.can_manage_chat is not None:
                data.update({"can_manage_chat": True})
            if permissions_class.can_post_messages is not None:
                data.update({"can_post_messages": True})
            if permissions_class.can_edit_messages is not None:
                data.update({"can_edit_messages": True})
            if permissions_class.can_delete_messages is not None:
                data.update({"can_delete_messages": True})
            if permissions_class.can_manage_voice_chats is not None:
                data.update({"can_manage_voice_chats": True})
            if permissions_class.can_restrict_members is not None:
                data.update({"can_restrict_members": True})
            if permissions_class.can_promote_members is not None:
                data.update({"can_promote_members": True})
            if permissions_class.can_change_info is not None:
                data.update({"can_change_info": True})
            if permissions_class.can_invite_users is not None:
                data.update({"can_invite_users": True})
            if permissions_class.can_pin_messages is not None:
                data.update({"can_pin_messages": True})
        else:
            return None
        if reply.reply_to_message_id is not None:
            data.update({"reply_to_message_id": reply.reply_to_message_id})
            data.update({"allow_sending_without_reply": True})
        try:
            req = requests.post(
                f"{self.base_url}{api_method}",
                data=data,
                files=files,
                timeout=OUTGOING_REQUESTS_TIMEOUT,
            )
        except requests.exceptions.RequestException:
            logging.error("An error occured sending the message request")
            return None
        logging.info("Sent message")
        if not req.ok:
            logging.error("Failed sending message - details: %s", req.json())
            return None
        return json.loads(req.content)

    def get_replies(self, message: Message) -> Optional[List]:
        """Checks if a bot command is triggered and gets its reply"""
        text = message.text
        if not text:
            return None
        messages: List[BotAction] = []
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
        while True:
            time.sleep(1)
            managers_actions = self.get_managers_actions()
            if managers_actions is None:
                continue
            for manager in managers_actions:
                for manager_trigger_messages_and_actions in manager:
                    for bot_action in manager_trigger_messages_and_actions[1]:
                        self.send_message_and_update_db(
                            manager_trigger_messages_and_actions[0], bot_action
                        )

    def handle_updates(self) -> None:
        """Handles the bot updates"""
        while True:
            updates = self.get_updates(offset=self.update_id) or {}
            for item in updates.get("result", []):
                logging.info("Processing updates")
                self.update_id = item["update_id"]
                # catching the text messages
                if "message" in item:
                    message = Message(
                        item["message"]["message_id"],
                        item["message"]["from"]["first_name"],
                        item["message"]["from"]["id"],
                        item["message"]["chat"]["id"],
                        None,
                        item["message"].get("reply_to_message", {}).get("message_id"),
                        item["message"]["from"].get("username", None),
                        False,
                        item["message"]["date"],
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
                        message.sender_username = item["message"][
                            "new_chat_member"
                        ].get("username", None)
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
                    message = Message(
                        item["callback_query"]["id"],
                        item["callback_query"]["from"]["first_name"],
                        item["callback_query"]["from"]["id"],
                        item["callback_query"]["message"]["chat"]["id"],
                        item["callback_query"]["data"],
                        item["callback_query"]["message"]["message_id"],
                        item["callback_query"]["from"].get("username", None),
                        False,
                    )
                    self.handle_callback_query(message)
            time.sleep(1)

    def start_bot(self) -> None:
        """Starts the bot"""
        managers_process = threading.Thread(target=self.handle_managers)
        updates_process = threading.Thread(target=self.handle_updates)
        managers_process.start()
        updates_process.start()
        managers_process.join()
        updates_process.join()
