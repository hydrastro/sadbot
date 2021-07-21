"""Sample/uwuspeak bot command"""
# these imports are optional:
import re
from sadbot.message_repository import MessageRepository

# these imports are required in every module:
from typing import Optional, List

# you need to import the handler type, every command is tied to just one type
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
# then you need to import the bot action type
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_IMAGE,
)

# the class name must be the pascal case of the module filename + "BotCommand"
class UwuBotCommand(CommandInterface):
    """This is the sample command bot command class"""

    # the constructor is NOT required. Anyway if the bot command need some
    # dependencies, they will be automatically injected through it
    def __init__(self, message_repository: MessageRepository):
        """Initializes the command class"""
        self.message_repository = message_repository

    @property
    def handler_type(self) -> str:
        """Here is the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Here is the regex that triggers this bot command"""
        regex = r"uwu(.*)?"
        return regex

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """This function can return some bot actions/replies that will  be sent later"""
        # this is an example on how you can process the message that triggered
        # the command to get a custom reply
        # here we are  getting the last message sent in the chat with the support of
        # a very useful module of sadbot we're injecting into this class
        # we could also have injected the direct database connection and retrieved
        # the last message directly
        previous_message = self.message_repository.get_previous_message(message, "^(?!\s*$).+")
        if previous_message is None:
            return None
        if previous_message.text is None:
            return None
        try:
            # uwu-mocking the message found
            reply_text = re.sub(r"(\w{3})", r"\1w", previous_message.text)
        except re.error:
            return None
        # here is how you open/set an image for the bot action
        reply_image_file = open("./sadbot/data/uwu.jpg", mode="rb")
        reply_image = reply_image_file.read()
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_IMAGE,
                reply_image=reply_image,
                reply_text=reply_text,
            ),
        ]
