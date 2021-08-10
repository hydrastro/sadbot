"""This module contains the Permissions dataclass"""

from dataclasses import dataclass
from typing import Optional


@dataclass  # pylint: disable=too-many-instance-attributes
class ChatPermissions:
    """ChatPermissions dataclass"""

    # ChatPermissions, restricted chat member:
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    # ChatPermissions, restricted chat member, administrator:
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None  # optional for administrator
    # administrator:
    can_be_edited: Optional[bool] = None
    can_manage_chat: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_manage_voice_chats: Optional[bool] = None
    can_post_messages: Optional[bool] = False  # optional for administrator
    can_edit_messages: Optional[bool] = False  # optional for administrator
    # kicked:
    ban_until_date: Optional[int] = None
