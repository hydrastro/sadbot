"""This module contains the Message class"""

from dataclasses import dataclass
from typing import Optional, List

MESSAGE_FILE_TYPE_PHOTO = 0
MESSAGE_FILE_TYPE_DOCUMENT = 1
MESSAGE_FILE_TYPE_VOICE = 2
MESSAGE_FILE_TYPE_VIDEO = 3
# and so on..


@dataclass
class Entity:
    """Telegram entity class"""

    offset: int
    length: int
    type: str


@dataclass
class Message:  # pylint: disable=too-many-instance-attributes
    """Message class"""

    message_id: int = 0
    sender_name: str = ""
    sender_id: int = 0
    chat_id: int = 0
    text: Optional[str] = None
    reply_id: Optional[int] = None
    sender_username: Optional[str] = None
    is_bot: Optional[bool] = False
    message_time: Optional[int] = 0
    file_type: Optional[int] = None
    file_id: Optional[str] = None
    mime_type: Optional[str] = None
    entities: Optional[List[Entity]] = None
