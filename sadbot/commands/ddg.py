"""Duckduckgo bot command"""
import urllib
from typing import Optional, List
import bs4
import requests

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class DdgBotCommand(CommandInterface):
    """This is the Duckduckgo bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching Duckduckgo commands"""
        return r"((!|\.)([Dd]{2}[Gg])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns reply for Duckduckgo command"""
        if message is None or message.text is None:
            return None
        query = " ".join(message.text.split(" ")[1:])
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0)"
            + "Gecko/20100101 Firefox/98.0",
        }
        url = "https://html.duckduckgo.com/html/"
        data = f"q={urllib.parse.quote(query)}&b=&kl=&df="
        try:
            req = requests.post(url, headers=headers, data=data)
            soup = bs4.BeautifulSoup(req.text, "html.parser")
        except requests.RequestException:
            print("HELP")
            return None
        results = soup.find_all("div", attrs={"class": "result"})
        counter = 1
        answer = f"Results from [Duck Duck Go](https://duckduckgo.com) for {query}:\n"
        for result in results:
            s_result = result.find_next("a", attrs={"class": "result__a"})
            link = s_result.attrs.get("href")
            title = s_result.text
            link = link.replace("https://", "")
            answer += f"{counter}. [{title}]({urllib.parse.quote(link)})\n"
            counter += 1
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=answer,
                reply_text_parse_mode="Markdown",
            )
        ]
