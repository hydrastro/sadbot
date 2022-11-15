"""OpenAI bot command"""
from typing import Optional, List
import random
import json

import requests
import openai

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.config import OPENAI_API_KEY
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_IMAGE


class OpenaiBotCommand(CommandInterface):
    """This is the sample command bot command class"""

    @property
    def handler_type(self) -> int:
        """Here is the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Here is the regex that triggers this bot command"""
        regex = r"((!|\.)([Oo][Pp][Ee][Nn][Aa][Ii])).*"
        return regex

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """This function can return some bot actions/replies that will  be sent later"""
        if message is None:
            return None
        with open(
            "./sadbot/assets/openai/all.json", mode="r", encoding="utf-8"
        ) as dictionary_stream:
            dictionary_content = dictionary_stream.read()
        dictionary = json.loads(dictionary_content)
        dictionary_length = len(dictionary)
        words = []
        for _ in range(3):
            words.append(dictionary[random.randint(0, dictionary_length)])
        try:
            openai.api_key = OPENAI_API_KEY
            reply_text = " ".join(words)
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=reply_text,
                temperature=0,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            reply_text += response["choices"][0]["text"]
            words = reply_text.split()
            reply_text = " ".join(sorted(set(words), key=words.index))
            response = openai.Image.create(prompt=reply_text, n=1, size="1024x1024")
            image_url = response["data"][0]["url"]
            response = requests.get(image_url, timeout=10)
            reply_image = response.content
        except Exception:  # pylint: disable=broad-except:
            with open("./sadbot/assets/uwu/uwu.jpg", mode="rb") as uwu_buffer:
                reply_image = uwu_buffer.read()
            reply_text = "An error occurred."
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_IMAGE,
                reply_image=reply_image,
                reply_text=reply_text,
            )
        ]
