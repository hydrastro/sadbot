"""Youtube Shorts bot command"""

from typing import Optional, List

import logging
import json
import random
import re
import requests
from pytube import YouTube

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE


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

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """
	        Scraps Youtube shorts
            selects a random video
            uses pytube to extract the direct download url
            formats a caption containing video information
            returns the result
        """
        headers = {
            "Accept-Language": "en-US",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        }
        try:
            req = requests.get(
                "https://www.youtube.com/hashtag/shorts", headers=headers, cookies={"CONSENT": "YES+42"}
            )
        except requests.exceptions.RequestException as exception:
            logging.error("An error occured while sending the youtube shorts request")
            logging.error(str(exception))
            return None
        if not req.ok:
            logging.warning("Failed to get youtube shorts data - details: %s", req.text)
            return None
        data = re.findall(re.compile('"content":{"richGridRenderer":(.*?)},"tabIdentifier":'), req.text)
        if data is None:
            logging.warning("Failed to get Youtube shorts data: regex gave no results.")
            return None

        
        try:
            json_data = json.loads(data[0])
            
            videos = json_data['contents']
            random_video = random.choice(videos)['richItemRenderer']['content']['videoRenderer']
            watch_url = "https://www.youtube.com/watch?v="+random_video['videoId']
            download_url = YouTube(watch_url).streams.get_highest_resolution().url
            title = random_video['title']['runs'][0]['text']
            channel = random_video['ownerText']['runs'][0]['text']
            channel_url = "https://www.youtube.com"+random_video['ownerText']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
            views =  random_video['viewCountText']['simpleText']
        except IndexError as exception:
            logging.warning("re.finall returned no results.")
            logging.warning(str(exception))
            return None
        except KeyError as exception:
            logging.error("An error occured while extracting the Youtube short data.")
            logging.error(f"key {exception} doesn't exist.")
            return None

        caption = f"{title}\n{watch_url}\n{views}\nSource: {channel}\n {channel_url}"
        
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
                reply_online_media_url=download_url,
                reply_text=caption
            )
        ]
