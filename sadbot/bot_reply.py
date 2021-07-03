"""This module contains the BotAction class"""

from typing import Optional
from dataclasses import dataclass
from io import BytesIO

BOT_ACTION_TYPE_REPLY_TEXT = 0
BOT_ACTION_TYPE_REPLY_IMAGE = 1
BOT_ACTION_TYPE_REPLY_AUDIO = 2
BOT_ACTION_TYPE_REPLY_FILE = 4
BOT_ACTION_TYPE_REPLY_VOICE = 5
BOT_ACTION_TYPE_KICK_USER = 6


@dataclass
class BotAction:
    """BotAction class"""

    reply_type: int = BOT_ACTION_TYPE_REPLY_TEXT
    reply_text: Optional[str] = None
    reply_text_parsemode: Optional[str] = None
    reply_image: Optional[BytesIO] = None
    reply_audio: Optional[BytesIO] = None
    reply_file: Optional[BytesIO] = None
    reply_voice: Optional[BytesIO] = None
    reply_kick_user_id: Optional[int] = None
