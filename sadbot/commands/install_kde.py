"""Anti-denk bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.commands.cope import CopeBotCommand
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_DELETE_MESSAGE
from sadbot.message_repository import MessageRepository


class InstallKdeBotCommand(CommandInterface):
    """This is the anti-denk bot command class"""

    def __init__(self, message_repository: MessageRepository) -> None:
        """Initializes the command"""
        self.message_repository = message_repository

    @property
    def handler_type(self) -> int:
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for trolling denk"""
        return r".*([Ii]|1)+?[Nn]+?([Ss]|5)+?[Tt]+?([Aa]|4)+?[Ll]+?(.+)?[Kk]+?[Dd]+?([Ee]|3)+?.*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """'Welcomes' a new user"""
        if message is None or message.text is None:
            return None
        replies = [
            BotAction(
                BOT_ACTION_TYPE_DELETE_MESSAGE,
                reply_delete_message_id=message.message_id,
            )
        ]
        cope_class = CopeBotCommand(self.message_repository)
        cope = CopeBotCommand.get_reply(cope_class, message)
        if cope is not None:
            replies += cope
        return replies
