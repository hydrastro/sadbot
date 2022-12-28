"""Playground bot command"""

from typing import Optional, List

import json
import re
import requests

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_TEXT,
)

languages = {
    "rust": "rs",
    "zig": "zig",
    "nim": "nim",
    "gcc": "c",
    "python": "py",
    "bash": "bash",
    "c++": "cpp",
    "go": "go",
    "csharp": "cs",
    "fortran": "f90",
}


class PlaygroundBotCommand(CommandInterface):
    """This is the playground bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return "MarkdownV2"

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching activity commands"""
        return r"(.|!)([pP][lL][aA][yY][gG][rR][oO][uU][nN][dD]|[Rr][Uu][Nn])(.|\s)*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Playground"""
        if (
            message is None
            or message.text is None
            or len(message.text) < 12
            or len(re.split(r"\s", message.text[12:], 1)) != 2
        ):
            return None
        split = re.split(r"\s", message.text[12:], 1)
        language = split[0]
        code = split[1]
        version = None
        found = False
        try:
            resp = requests.get("https://emkc.org/api/v2/piston/runtimes")
            for element in resp.json():
                if language in element["aliases"] or language == element["language"]:
                    language = element["language"]
                    version = element["version"]
                    found = True
                    break
        except (requests.RequestException, json.JSONDecodeError):
            return None
        if found is False:
            return None
        extension = languages.get(language)
        if extension is not None:
            file_name = "random." + extension
        else:
            file_name = "random"
        try:
            payload = {
                "language": language,
                "version": version,
                "files": [
                    {
                        "name": file_name,
                        "content": code,
                    }
                ],
            }
            resp = requests.post(
                "https://emkc.org/api/v2/piston/execute", data=json.dumps(payload)
            )
            body = resp.json()
            text = ""
            error = False
            if "compile" in body and body["compile"]["code"] != 0:
                text = body["compile"]["stderr"]
                error = True
            else:
                if "run" not in body:
                    return None
                text = body["run"]["output"]
        except (requests.RequestException, json.JSONDecodeError):
            return None
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=f"{'Error' if error else 'Output'}:\n{text}",
                reply_to_message_id=message.message_id,
            ),
        ]
