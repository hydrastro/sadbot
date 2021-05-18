""" This module contains the Message class """

from typing import Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Message class"""

    id: int = 0  # pylint: disable=invalid-name
    sender_name: str = ""
    sender_id: int = 0
    chat_id: int = 0
    text: str = ""
    reply_id: Optional[int] = None
