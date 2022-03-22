"""Weed bot command"""

from typing import Optional, List
import random

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


class WeedBotCommand(CommandInterface):
    """This is the weed bot command class"""

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching lenovo commands"""
        return r".*([Ww][Aa][Nn][Tt]|[Ll][Ii][Kk][Ee]).*([Ww][Ee]{2}[Dd]).*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Politely refuses weed while staying cool cause my brain already smooth"""
        # Proudly stolen from https://archive.ph/dR5Df
        replies = [
            "Are you kidding me? Grow up!",
            "Ganja is for goons, no thanks.",
            "Get a jab you hippie westoid.",
            "You need to go to jail, hempo",
            "My dad told me better, no way.",
            "Grass is crass, also gross! No!",
            "Uhhh... no thanks loser!",
            "Get away from me, THC addict.",
            "Yeah right, I'm way too smart.",
            "Let me think...  No way, never.",
            "No, You are trash if you take.",
            "Back off, bucko, You're bad.",
            "I would rather not, okay?",
            "Injecting weed is for dummies",
            "I will never do one take",
            "Absolutely not, I love myself",
            "Get a grip you sativa snorter!",
            "Bugger off, you bang addict!",
            "I will use my taser on you",
            "What do I look like? A failure?",
            "Nah, bongs are wrong.",
            "No way! Hemp is horrible!",
            "I'd rather not be a cannibal.",
            "I don't think so, I'm nice.",
            "I was raised right, I won't light.",
            "I'd like to keep my job, thanks.",
            "You wish, pat junker! Back off!",
            "I'm calling the Coast Guard.",
            "No takes for me. I'm cool.",
            "Leave me be, you blunt blazer!",
            "No, I'm as clean as a whistle.",
            'That\'s a death "reach". No.',
            "I'll pass on your pot offer.",
            "Cannabis is crap, you cretin?",
            "Pish posh, pot is for the birds!",
            "Nope. THC is not for me.",
            "Step out of my zone, now.",
            "Get off my case, weed stoner.",
            "Nuh uh, I respect the police.",
            "Lay off, I listen to the law.",
            "NO! Blunts are for bad men.",
            "I'd rather not die. Takes kill.",
            "No, weeds are for whacking.",
            "Marijuana is for morons, ok?",
            "Are you serious? Get a life!",
            'You\'re dumb if you do "dank".',
            "Stoners are loners. I'm good.",
            "Nope! Spliffs are for wimps!",
            "No, man, I follow MMYV.",
        ]
        return [
            BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=random.choice(replies))
        ]
