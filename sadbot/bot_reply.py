"""This module contains the BotReply class"""

from typing import Optional
from dataclasses import dataclass
from io import BytesIO

BOT_REPLY_TYPE_TEXT = 0
BOT_REPLY_TYPE_IMAGE = 1
BOT_REPLY_TYPE_AUDIO = 2
BOT_REPLY_TYPE_FILE = 4
BOT_REPLY_TYPE_VOICE = 5
BOT_REPLY_TYPE_KICK_USER = 6


@dataclass
class BotReply:
    """BotReply class"""

    reply_type: int = BOT_REPLY_TYPE_TEXT
    reply_text: Optional[str] = None
    reply_text_parsemode: Optional[str] = None
    reply_image: Optional[BytesIO] = None
    reply_audio: Optional[BytesIO] = None
    reply_file: Optional[BytesIO] = None
    reply_voice: Optional[BytesIO] = None
    reply_kick_user_id: Optional[int] = None
