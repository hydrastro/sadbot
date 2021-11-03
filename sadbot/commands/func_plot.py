"""Function plot bot command"""

import os
from typing import Optional, List
import random
from sympy.plotting import plot
from sympy.parsing.sympy_parser import parse_expr

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_REPLY_TEXT,
)
from sadbot.functions import safe_cast


class FuncPlotBotCommand(CommandInterface):
    """This is the sed bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching function plot commands"""
        return r"((!|\.)([Pp][Ll][Oo][Tt])).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Plots"""
        if message is None or message.text is None:
            return None
        split = message.text.split()
        if len(split) < 2:
            return self.exit_message("Yo insert an expression.")
        lower_bound = -50
        upper_bound = 50
        if len(split) > 3:
            lower_bound = safe_cast(split[2], float, lower_bound)
            upper_bound = safe_cast(split[3], float, upper_bound)
        if lower_bound >= upper_bound:
            return self.exit_message("The ranges you have entered are not valid.")
        try:
            da_plot = plot(
                parse_expr(split[1]),
                xlim=[lower_bound, upper_bound],
                ylim=[lower_bound, upper_bound],
                show=False,
            )
        except SyntaxError:
            return self.exit_message("An error occured evaluating the expression.")
        name = str(random.randint(14124124124, 1412412412414124124124)) + ".png"
        da_plot.save(name)
        with open(name, "rb") as file:
            byte_array = file.read()
        os.remove(name)
        return [
            BotAction(
                BOT_ACTION_TYPE_REPLY_IMAGE,
                reply_image=byte_array,
            )
        ]

    @staticmethod
    def exit_message(reply_text: str) -> Optional[List[BotAction]]:
        """Just returns a message with a specified text"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
