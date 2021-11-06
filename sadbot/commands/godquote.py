"""God quote bot command"""

from typing import Optional, List
import random
import json

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.functions import safe_cast


class GodquoteBotCommand(CommandInterface):
    """This is the God quote bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Gg][Oo][Dd][Qq][Uu][Oo][Tt][Ee])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns God words"""
        if message is None or message.text is None:
            return None
        with open(
            "./sadbot/assets/godquote/quran_arabic.json", mode="r", encoding="utf-8"
        ) as god_file_arabic, open(
            "./sadbot/assets/godquote/quran_english.json", mode="r", encoding="utf-8"
        ) as god_file_english:
            god_book_arabic = json.load(god_file_arabic)
            god_book_english = json.load(god_file_english)
            split = message.text.split()
            len_split = len(split)
            chapter = random.randint(1, len(god_book_arabic))
            verse = random.randint(0, len(god_book_arabic[f"{chapter}"]) - 1)
            if len_split > 1:
                chapter = safe_cast(split[1], int, chapter)
            if len_split > 2:
                verse = random.randint(1, len(god_book_arabic[f"{chapter}"]))
                verse = safe_cast(split[2], int, verse)
                verse -= 1
            arabic_quote = god_book_arabic[f"{chapter}"][verse]["text"]
            english_quote = god_book_english[f"{chapter}"][verse]["text"]
            verse += 1
            reply_text = f"{chapter}, {verse}:\n{arabic_quote}\n{english_quote}"
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
