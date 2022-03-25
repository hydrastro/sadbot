"""Help bot command"""

from typing import Optional, List

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class HelpBotCommand(CommandInterface):
    """This is the help bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the help command"""
        return r"(\.)([Hh][Ee][Ll][Pp]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns the help message for the bot"""
        if message is None:
            return None
        help_message = "\n".join(
            [
                "The bot has the following commands:",
                "- activity - displays an activity graph for the group",
                "- ban <user> or reply to message - bans an user (for admins)",
                "- beaver - only works in a few groups and returns a text message from beaver"
                ""
                "- bible <verse> - returns the text of that verse",
                "- thread - closes a thread :0",
                "- setconfig - sets default configs (for admins)",
                "- cringe - returns a random feed from a cringe lord",
                "- ddg <query> - returns search results for a query from duck duck go",
                "- fbi - anyway",
                "- getchatid - returns the id of the chat",
                "- getid <user> or reply to message - gets the id of the user",
                "- gitpull - only for the bot owner, the id must be hardcoded in config",
                "- godquote <verse> - returns a verse from Quran",
                "- help - returns this help message",
                "- hug <user> or reply to message - hugs a player aka sends a video",
                "- list <with its subcommands> - write 'list' for more details",
                "- mute <user> or reply to user - mutes an user (for admins)",
                "- pasta - prints a copypasta",
                "- ping - pings the bot (useful for checking if the bot is up)",
                "- playground <language> <code> - uses piston api to run the code",
                "- plot - plots a graph",
                "- rand (x, y) - returns a random number from the interval [x, y]",
                "- remindme <duration> - the bot pings you after that period of time",
                "- roll - returns a random number between 0 and 9",
                "- roulette - test your luck",
                "- query - query the database (only for bot owner)",
                "- goschizo - have fun",
                "- s/<a>/<b>/(g?) - sed aka replaces a with b, use g for global replacement",
                "- seen - returns the last message of an user stored in the database",
                "- shorts - return a random short from ytb",
                "- slap - have fun",
                "- spoiler - spoils an image",
                "- tr/trl <language> - translates the text of the message you reply to",
                "- unmute - unmutes an user (for admins)",
                "- warn - warns an user (for admins)",
                "- wc - word count of a message",
                "- ytdlp - downloads a video from youtube",
                "The bot has a few easter eggs, have fun finding them.",
                "The prefix for sadbot is `.`, for example `.shorts`",
                "The source code is at [sadbot](https://github.com/hydrastro/sadbot).",
            ]
        )
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=help_message,
                reply_text_parse_mode="Markdown",
            )
        ]
