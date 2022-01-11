"""Function plot bot command"""

import os
import re
from typing import Optional, List, Any
import random
from sympy.plotting import plot, plot3d
from sympy.parsing.maxima import parse_maxima
from sympy import symbols

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_IMAGE,
    BOT_ACTION_TYPE_REPLY_TEXT,
)


class PlotBotCommand(CommandInterface):
    """This is the plot bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching function plot commands"""
        return r"((!|\.)([Pp][Ll][Oo][Tt])([3][Dd])?)\s.*"

    def get_reply(  # pylint: disable=too-many-locals
        self, message: Optional[Message] = None
    ) -> Optional[List[BotAction]]:
        """Plots"""
        if message is None or message.text is None:
            return None
        if "3d" in message.text:
            plot_3d = True
            split = message.text[8:].split(",")
        else:
            plot_3d = False
            split = message.text[6:].split(",")
        ranges = re.split("[Rr][Aa][Nn][Gg][Ee]", split[-1])
        split[-1] = ranges[0]
        expressions = []
        xlim = None
        ylim = None
        range_x = None
        range_y = None
        x_var, y_var = symbols("x y")
        if len(ranges) > 1:
            temp = ranges[-1].split()
            if len(temp) < 3:
                return self.exit_message(
                    "Invalid ranges. Format: `xmin xmax ymin ymax`."
                )
            xlim = (temp[0], temp[1])
            ylim = (temp[2], temp[3])
            range_x = (x_var, temp[0], temp[1])
            range_y = (y_var, temp[2], temp[3])
        try:
            for expression in split:
                expressions.append(parse_maxima(expression))
            if expressions == []:
                return self.exit_message("Please enter at least one valid expression.")
            if plot_3d:
                temp_exp = []
                for expression in expressions:
                    temp2: List[Any] = [expression]
                    if range_x is not None and range_y is not None:
                        temp2.append(range_x)
                        temp2.append(range_y)
                    temp_exp.append(tuple(temp2))
                da_plot = plot3d(*temp_exp, show=False)
            else:
                da_plot = plot(*expressions, xlim=xlim, ylim=ylim, show=False)
        except (SyntaxError, ValueError, TypeError) as caught_exception:
            return self.exit_message(
                f"An error occured evaluating the expression.\nDetails: {str(caught_exception)}"
            )
        name = (
            str(random.randint(14_124_124_124, 1_412_412_412_414_124_124_124)) + ".png"
        )
        da_plot.save(name)
        with open(name, "rb") as file:
            byte_array = file.read()
        os.remove(name)
        return [BotAction(BOT_ACTION_TYPE_REPLY_IMAGE, reply_image=byte_array)]

    @staticmethod
    def exit_message(reply_text: str) -> Optional[List[BotAction]]:
        """Just returns a message with a specified text"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
