"""Hug bot command"""
from typing import Optional, List

from sadbot.message_repository import MessageRepository

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message

from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_VIDEO


class HugBotCommand(CommandInterface):
    """This is the sample command bot command class"""

    def __init__(self, message_repository: MessageRepository):
        """Initializes the command class"""
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        """Here is the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Here is the regex that triggers this bot command"""
        return "hug.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """This function can return some bot actions/replies that will  be sent later"""
        if message is None:
            return None
        if message.reply_id is not None:
            previous_message = self.message_repository.get_message_from_id(
                message.reply_id
            )
            if previous_message is None:
                return None
            r_username = (
                previous_message.sender_username or previous_message.sender_name
            )
        else:
            if message.text is None:
                return None
            if len(message.text) < 5:
                return None
            username = message.text[4:]
            r_username = username.replace("@", " ")
            r_username = r_username.replace(" ", "")
        s_username = message.sender_username or message.sender_name
        text = f"@{s_username} hugs @{r_username}"
        with open("sadbot/assets/hug/hug.mp4", "rb") as file:
            hug = file.read()
        return [
            BotAction(BOT_ACTION_TYPE_REPLY_VIDEO, reply_video=hug, reply_text=text)
        ]
