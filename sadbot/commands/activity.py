"""Activity bot command"""
import io
from typing import Optional, List
import time
import math
from datetime import datetime
import requests
import matplotlib.pyplot as plt

from sadbot.app import App
from sadbot.functions import convert_to_days

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_REPLY_TEXT,
)


class ActivityBotCommand(CommandInterface):
    """This is the activity bot command class"""

    def __init__(self, app: App, message_repository: MessageRepository):
        """Initializes the activity command"""
        self.app = app
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching activity commands"""
        return r"(.|!)([aA][cC][tT][iI][vV][iI][tT][yY]).*"

    def get_image(self, chat_id: int, message_text: str) -> bytes:
        """Get image lol"""
        dates: List[datetime] = []
        counts: List[int] = []
        if len(message_text) == 9:
            time_string = "1w"
        else:
            time_string = message_text[9:]

        days = convert_to_days(time_string)
        if days <= 1:
            days = 2

        days = min(days, 365)

        end: int = math.ceil(time.time())
        for _ in range(0, days):
            begin = end - 86400
            count = self.message_repository.get_count_messages_sent_in_range(
                begin, end, chat_id
            )
            dates.append(datetime.utcfromtimestamp(end))
            counts.append(count)
            end = begin
        dates.reverse()
        counts.reverse()
        with plt.style.context(plt.style.library["Solarize_Light2"]):
            plt.rcParams["figure.figsize"] = (16, 4)
            plt.plot(dates, counts, label="count")
            plt.xlabel("time")
            plt.ylabel("count")
            plt.legend(frameon=False)
            bytes_io = io.BytesIO()
            plt.savefig(bytes_io, dpi=300, format="png")
        bytes_io.seek(0)
        image = bytes_io.read()
        return image

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Activity"""
        if message is None or message.text is None:
            return None
        image = self.get_image(message.chat_id, message.text)
        try:
            req = requests.post("https://oshi.at", files={"activity.png": image})
            url = req.text.splitlines()[1].split(" ")[1]
        except (requests.ConnectionError, IndexError):
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_IMAGE,
                    reply_image=image,
                )
            ]
        reply_text = (
            """Here's the chat activity, you can click on the link to see the """
            + f"""full quality image:\n{url}"""
        )
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
            ),
        ]
