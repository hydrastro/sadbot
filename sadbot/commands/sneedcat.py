"""Sneedcat bot command"""

import random
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass

import requests
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_PHOTO_ONLINE,
    BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
)

API_URL = "https://api.twitter.com"
ACTIVATE_URL = f"{API_URL}/1.1/guest/activate.json"
TIMELINE_API_URL = f"{API_URL}/2/timeline"
MEDIA_TIMELINE_URL = f"{TIMELINE_API_URL}/media"
ID = "1430695610009542656"

# Authorization key stolen from Nitter
AUTH = (
    "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3D"
    + "TYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
)


def gen_headers(token: str) -> Dict[str, str]:
    """Generates headers for fetch_raw function"""
    return {
        "connection": "keep-alive",
        "authorization": AUTH,
        "content-type": "application/json",
        "x-guest-token": token,
        "x-twitter-active-user": "yes",
        "authority": "api.twitter.com",
        "accept-encoding": "gzip",
        "accept-language": "en-US,en;q=0.9",
        "accept": "*/*",
        "DNT": "1",
    }


def fetch_raw(url: str, token: str) -> dict:
    """Fetches an url"""
    headers = gen_headers(token)
    req = requests.get(url, headers=headers)
    return req.json()


def fetch_token() -> str:
    """Gets a token from twitter"""
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip",
        "accept-language": "en-US,en;q=0.5",
        "connection": "keep-alive",
        "authorization": AUTH,
    }
    resp = requests.post(ACTIVATE_URL, headers=headers)
    return resp.json()["guest_token"]


class MediaType(Enum):
    """An enum for twitter's media type"""

    PHOTO = 1
    VIDEO = 2


@dataclass
class Media:
    """A class representing media"""

    media_type: MediaType
    title: str
    url: str


def handle_media(title: str, node: dict) -> Optional[Media]:
    """Return a media file from a json node representing twitter's media"""
    if node["type"] == "photo":
        media = Media(MediaType.PHOTO, title, node["media_url_https"])
    elif node["type"] == "video":
        variants = node["video_info"]["variants"]
        biggest = variants[0]
        for variant in variants:
            if "bitrate" in variant:
                if variant["bitrate"] > biggest["bitrate"]:
                    biggest = variant
        media = Media(MediaType.VIDEO, title, biggest["url"])
    else:
        return None
    return media


class SneedcatBotCommand(CommandInterface):
    """This is the sneedcat bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching sneedcat commands"""
        return r"([.]|!)[Ss][Nn][Ee]{2}[Dd][Cc][Aa][Tt]"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Print a sneedcat"""
        if message is None:
            return None
        token = fetch_token()

        url = f"{MEDIA_TIMELINE_URL}/{ID}.json"
        tweets = fetch_raw(url, token)["globalObjects"]["tweets"]
        data = []
        for tweet_id in tweets:
            tweet = tweets[tweet_id]
            title = tweet["text"]
            if "media" in tweet["entities"]:
                all_media = tweet["entities"]["media"]
                for entity in all_media:
                    media = handle_media(title, entity)
                    if not media:
                        continue
                    data.append(media)
            if "extended_entities" in tweet and "media" in tweet["extended_entities"]:
                all_media = tweet["extended_entities"]["media"]
                for entity in all_media:
                    media = handle_media(title, entity)
                    if not media:
                        continue
                    data.append(media)
        media = random.choice(data)

        if media.media_type == MediaType.PHOTO:
            action = BotAction(
                reply_type=BOT_ACTION_TYPE_REPLY_PHOTO_ONLINE,
                reply_online_photo_url=media.url,
                reply_text=media.title,
            )
        else:
            action = BotAction(
                reply_type=BOT_ACTION_TYPE_REPLY_VIDEO_ONLINE,
                reply_online_media_url=media.url,
                reply_text=media.title,
            )
        return [action]
