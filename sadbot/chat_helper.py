"""Chat helper class"""
import json
from typing import Optional, Dict, List
import requests

from sadbot.config import (
    OUTGOING_REQUESTS_TIMEOUT,
)
from sadbot.permissions import Permissions

CHAT_HELPER_MEMBER_STATUS_CREATOR = 0
CHAT_HELPER_MEMBER_STATUS_ADMIN = 1
CHAT_HELPER_MEMBER_STATUS_USER = 2  # member
CHAT_HELPER_MEMBER_STATUS_LEFT = 3
CHAT_HELPER_MEMBER_STATUS_BANNED = 4  # kicked
CHAT_HELPER_MEMBER_STATUS_RESTRICTED = 5


class ChatHelper:
    """This is the chat helper class"""

    def __init__(self, base_url: str):
        """Initializes the chat helper class"""
        self.base_url = base_url

    def foo(self, chat_id: int) -> Optional[List]:
        """Gets a chat member"""
        data = {"chat_id": chat_id}
        api_method = "getChatAdministrators"
        req = requests.post(
            f"{self.base_url}{api_method}",
            data=data,
            timeout=OUTGOING_REQUESTS_TIMEOUT,
        )
        if not req.ok:
            print(f"Failed sending message - details: {req.json()}")
            return None
        return json.loads(req.content)

    def get_chat_permissions_json(self, chat_id: int, user_id: int = None) -> Optional[List]:
        """Gets a chat member"""
        data = {"chat_id": chat_id}
        api_method = "getChat"
        if user_id is not None:
            api_method = "getChatMember"
            data.update({"user_id": user_id})
        req = requests.post(
            f"{self.base_url}{api_method}",
            data=data,
            timeout=OUTGOING_REQUESTS_TIMEOUT,
        )
        if not req.ok:
            print(f"Failed sending message - details: {req.json()}")
            return None
        return json.loads(req.content)

    def get_user_permissions(self, chat_id: int, user_id: int) -> Optional[List]:
        data = self.get_chat_permissions_json(chat_id, user_id)
        data = data["result"]
        if data is None or "status" not in data:
            return None
        status = data["status"]
        if status == "creator":
            return [CHAT_HELPER_MEMBER_STATUS_CREATOR]
        if status == "left":
            return [CHAT_HELPER_MEMBER_STATUS_LEFT]
        if status == "member":
            return [CHAT_HELPER_MEMBER_STATUS_USER, self.get_chat_permissions(chat_id)]
        if status == "kicked":
            permissions = Permissions(ban_until_date=data.get("until_date", 0))
            return [CHAT_HELPER_MEMBER_STATUS_BANNED, permissions]
        permissions = Permissions(
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
            return [CHAT_HELPER_MEMBER_STATUS_ADMIN, permissions]
        return [CHAT_HELPER_MEMBER_STATUS_RESTRICTED, permissions]

    def get_chat_permissions(self, chat_id: int) -> Optional[Permissions]:
        data = self.get_chat_permissions_json(chat_id)
        print(data)
        if data is None:
            return None
        if "result" not in data or "permissions" not in data["result"]:
            return None
        permissions = data["result"]["permissions"]
        return Permissions(
            can_send_messages=permissions.get("can_send_messages", False),
            can_send_media_messages=permissions.get("can_send_media_messages", False),
            can_send_polls=permissions.get("can_send_polls", False),
            can_send_other_messages=permissions.get("can_send_other_messages", False),
            can_add_web_page_previews=permissions.get("can_add_web_page_previews", False),
            can_change_info=permissions.get("can_change_info", False),
            can_invite_users=permissions.get("can_invite_users", False),
            can_pin_messages=permissions.get("can_pin_messages", False),
        )

    @staticmethod
    def get_list_dict_permissions(permissions: Permissions) -> List[Dict]:
        return [
            {
                "can_send_messages": permissions.can_send_messages or False,
                "can_send_media_messages": permissions.can_send_media_messages or False,
                "can_send_polls": permissions.can_send_polls or False,
                "can_send_other_messages": permissions.can_send_other_messages or False,
                "can_add_web_page_previews": permissions.can_add_web_page_previews or False,
                "can_change_info": permissions.can_change_info or False,
                "can_invite_users": permissions.can_invite_users or False,
                "can_pin_messages": permissions.can_pin_messages or False,
            }
        ]
