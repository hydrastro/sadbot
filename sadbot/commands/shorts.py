"""Youtube Shorts bot command"""

from typing import Optional, List, Dict, Tuple

import logging
import random
import json
import re
import os

import requests
from yt_dlp import YoutubeDL

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_VIDEO,
    BOT_ACTION_TYPE_REPLY_TEXT,
)


class ShortsBotCommand(CommandInterface):
    """This is the Youtube Shorts bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching ping commands"""
        return r"((!|\.)([Ss][Hh][Oo][Rr][Tt][Ss])).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return "MarkdownV2"

    @staticmethod
    def get_request_headers() -> Dict:
        """Returns the request headers"""
        return {
            "Accept-Language": "en-US",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        }

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Scraps Youtube shorts
        selects a random video
        uses ytdlp to download the url
        formats a caption containing video information
        returns the result
        """
        try:
            req = requests.get(
                "https://www.youtube.com/hashtag/shorts",
                headers=self.get_request_headers(),
                cookies={"CONSENT": "YES+42"},
            )
        except requests.exceptions.RequestException as exception:
            logging.error("An error occured while sending the youtube shorts request")
            logging.error("%s", str(exception))
            return None
        if not req.ok:
            logging.warning("Failed to get youtube shorts data - details: %s", req.text)
            return None
        data = self.extract_data(req.text)
        if data is None:
            return None
        caption, watch_url = data
        file_name = str(random.randint(10000000000, 35000000000))
        if not self.save_video(file_name, watch_url):
            return [
                BotAction(
                    BOT_ACTION_TYPE_REPLY_TEXT,
                    reply_text="Something went wrong",
                )
            ]
        with open(file_name, "rb") as file:
            buf = file.read()
        os.remove(file_name)
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO,
                reply_video=buf,
                reply_text=caption,
            )
        ]

    @staticmethod
    def save_video(file_name: str, watch_url: str) -> bool:
        """
        Saves the video
        """
        ydl_opts = {
            "format": "(mp4)[filesize<50M]",
            "outtmpl": file_name,
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([watch_url])
                return True
            # pylint: disable=W0702
            except:
                return False

    @staticmethod
    def extract_data(text: str) -> Optional[Tuple[str, str]]:
        """
        Extract the data from a youtube entry
        """
        data = re.findall(
            re.compile('"content":{"richGridRenderer":(.*?)},"tabIdentifier":'),
            text,
        )
        if data is None:
            logging.warning("Failed to get Youtube shorts data: regex gave no results.")
            return None

        try:
            random_video = random.choice(json.loads(data[0])["contents"])[
                "richItemRenderer"
            ]["content"]["videoRenderer"]
            watch_url = "https://www.youtube.com/watch?v=" + random_video["videoId"]
            title = random_video["title"]["runs"][0]["text"]
            channel = random_video["ownerText"]["runs"][0]["text"]
            channel_url = (
                "https://www.youtube.com"
                + random_video["ownerText"]["runs"][0]["navigationEndpoint"][
                    "commandMetadata"
                ]["webCommandMetadata"]["url"]
            )
            views = random_video["viewCountText"]["simpleText"]
        except IndexError as exception:
            logging.warning("re.finall returned no results.")
            logging.warning(str(exception))
            return None
        except KeyError as exception:
            logging.error("An error occured while extracting the Youtube short data.")
            logging.error("Key %s doesn't exist.", exception)
            return None
        return (
            f"[{title}]({watch_url})\n{views}\nSource: {channel}\n {channel_url}",
            watch_url,
        )
