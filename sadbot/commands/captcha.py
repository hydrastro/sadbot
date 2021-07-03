"""Captcha bot command"""

# READ THIS
# This isn't really a bot command, so it should be moved somewhere else I guess
# The captcha handling class should be placed somewhere else in the main dir
# and the rest (new user and inline keyboard/text reply handling) should probably
# be splitted in two. I don't know if I should write an interface for handling all those cases

import sqlite3
from typing import Optional, List, Tuple
from os import path
import random
from PIL import Image, ImageFont, ImageDraw

from sadbot.command_interface import CommandInterface
from sadbot.message import Message
from sadbot.bot_reply import BotReply, BOT_REPLY_TYPE_IMAGE, BOT_REPLY_TYPE_KICK_USER
from sadbot.config import (
    CAPTCHA_BACKGROUND_COLOR,
    CAPTCHA_TEXT_COLOR,
    CAPTCHA_LINES_COLOR,
    CAPTCHA_DOTS_COLOR,
    CAPTCHA_CHARACTERS,
    CAPTCHA_WIDTH,
    CAPTCHA_HEIGHT,
    CAPTCHA_FONT,
    CAPTCHA_FONT_SIZE,
    CAPTCHA_MAX_ROTATION_ANGLE,
    CAPTCHA_LETTER_TOP_PADDING,
    CAPTCHA_LETTER_LEFT_PADDING,
    CAPTCHA_LINES_NUMBER,
    CAPTCHA_DOTS_NUMBER,
    CAPTCHA_LENGTH,
    CAPTCHA_EXPIRATION,
    CAPTCHA_RANDOMIZE_TEXT_COLORS,
    CAPTCHA_RANDOMIZE_LINES_COLORS,
    CAPTCHA_RANDOMIZE_DOTS_COLORS,
    CAPTCHA_LINES_START_FROM_BORDER,
    CAPTCHA_USE_BORDER_LINEAR_RANDOMNESS,
)


def get_captcha_table_creation_query() -> str:
    return """
    CREATE TABLE IF NOT EXISTS captchas (
      CaptchaID text,
      CaptchaText text
    )
    """


class Captcha:
    """Captcha class"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the captcha class"""
        self.con = con
        self.con.execute(get_captcha_table_creation_query())

    @staticmethod
    def get_random_color(self) -> Tuple[int, int, int]:
        """Returns a random RGB color as a list"""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def verify_captcha(self, captcha_id: str, captcha_text: str) -> bool:
        """Verifies if a given captcha is in the database"""
        cur = self.con.cursor()
        query = """
          SELECT
            CaptchaID,
            CaptchaText
          FROM
            captchas
          WHERE CaptchaID = ? AND CaptchaText = ?
        """
        params = [captcha_id, captcha_text]
        cur.execute(query, params)
        data = cur.fetchone()
        return data is not None

    @staticmethod
    def get_random_border_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Returns some random coordinates in the border of the image"""
        random_boolean = bool(random.getrandbits(1))
        if CAPTCHA_USE_BORDER_LINEAR_RANDOMNESS:
            rand = random.randint(CAPTCHA_WIDTH + CAPTCHA_HEIGHT)
            if rand <= x:
                x = rand
                y = CAPTCHA_HEIGHT if random_boolean else 0
            else:
                x = CAPTCHA_WIDTH if random_boolean else 0
                y = rand - CAPTCHA_WIDTH
        else:
            another_random_boolean = bool(random.getrandbits(1))
            if random_boolean:
                x = CAPTCHA_WIDTH if another_random_boolean else 0
                y = random.randint(0, CAPTCHA_HEIGHT)
            else:
                x = random.randint(0, CAPTCHA_WIDTH)
                y = CAPTCHA_HEIGHT if another_random_boolean else 0
        return x, y

    @staticmethod
    def get_captcha_string(self) -> str:
        return "".join(random.choice(CAPTCHA_CHARACTERS) for _ in range(CAPTCHA_LENGTH))

    def get_captcha(self, captcha_id: str):
        captcha_text = self.get_captcha_string()
        self.insert_captcha_into_db(captcha_id, captcha_text)
        return self.get_captcha_image(captcha_text)

    def insert_captcha_into_db(self, captcha_id: str, captcha_text: str) -> None:
        """Inserts a message into the database"""
        query = """
          INSERT INTO captchas (
            CaptchaText,
            CaptchaID
          ) VALUES (?, ?)
        """
        self.con.execute(
            query,
            (captcha_id, captcha_text),
        )
        self.con.commit()
        return

    def get_captcha_image(self, captcha_text: str):
        """Generates a cool captcha and returns it as a image"""
        background_color = (
            self.get_random_color()
            if CAPTCHA_BACKGROUND_COLOR is None
            else CAPTCHA_BACKGROUND_COLOR
        )
        text_color = (
            self.get_random_color()
            if CAPTCHA_TEXT_COLOR is None
            else CAPTCHA_TEXT_COLOR
        )
        lines_color = (
            self.get_random_color()
            if CAPTCHA_LINES_COLOR is None
            else CAPTCHA_LINES_COLOR
        )
        dots_color = (
            self.get_random_color()
            if CAPTCHA_DOTS_COLOR is None
            else CAPTCHA_DOTS_COLOR
        )
        piece_width = int(CAPTCHA_WIDTH / CAPTCHA_LENGTH)
        font = ImageFont.truetype(CAPTCHA_FONT, CAPTCHA_FONT_SIZE)
        image = Image.new("RGB", (CAPTCHA_WIDTH, CAPTCHA_HEIGHT), background_color)
        offset = 0
        for character in captcha_text:
            if CAPTCHA_RANDOMIZE_TEXT_COLORS:
                text_color = self.get_random_color()
            character_image = Image.new(
                "RGBA", (piece_width, CAPTCHA_HEIGHT), background_color
            )
            draw = ImageDraw.Draw(character_image)
            draw.text(
                (CAPTCHA_LETTER_LEFT_PADDING, CAPTCHA_LETTER_TOP_PADDING),
                character,
                fill=text_color,
                font=font,
            )
            character_image = character_image.rotate(
                random.randint(-CAPTCHA_MAX_ROTATION_ANGLE, CAPTCHA_MAX_ROTATION_ANGLE),
                fillcolor=background_color,
            )
            image.paste(character_image, (offset, 0))
            offset += character_image.size[0]
        for i in range(0, CAPTCHA_DOTS_NUMBER):
            draw = ImageDraw.Draw(image)
            if CAPTCHA_RANDOMIZE_DOTS_COLORS:
                dots_color = self.get_random_color()
            draw.point(
                (random.randint(0, image.width), random.randint(0, image.height)),
                dots_color,
            )
        for i in range(0, CAPTCHA_LINES_NUMBER):
            if CAPTCHA_LINES_START_FROM_BORDER:
                foo = self.get_random_border_coordinates()
                x0 = foo[0]
                y0 = foo[1]
                foo = self.get_random_border_coordinates()
                x1 = foo[0]
                y1 = foo[1]
            else:
                x0 = random.randint(0, CAPTCHA_WIDTH)
                y0 = random.randint(0, CAPTCHA_HEIGHT)
                x1 = random.randint(0, CAPTCHA_WIDTH)
                y1 = random.randint(0, CAPTCHA_HEIGHT)
            draw = ImageDraw.Draw(image)
            if CAPTCHA_RANDOMIZE_LINES_COLORS:
                lines_color = self.get_random_color()
            draw.line((x0, y0, x1, y1), fill=lines_color, width=1)
        return image


class CaptchaBotCommand(CommandInterface):
    """This is the captcha bot command class"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the captcha command"""
        self.captcha = Captcha(con)

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching new users"""
        return r"test"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotReply]]:
        """Returns a captcha or a command to kick a "user" who failed it"""
        return [BotReply(BOT_REPLY_TYPE_IMAGE)]

    def kick_user(self, user_id: int) -> Optional[BotReply]:
        return

    def get_captcha(self, captcha: str, filename: str) -> Optional[BotReply]:
        return
