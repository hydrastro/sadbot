import sqlite3
from typing import Optional, Tuple
import random
from PIL import Image, ImageFont, ImageDraw

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
    CAPTCHA_LINE_WIDTH,
)


def get_captcha_table_creation_query() -> str:
    """ "Returns the query for creating the captchas table"""
    return """
    CREATE TABLE IF NOT EXISTS captchas (
      CaptchaID text,
      CaptchaText text,
      Expiration timestamp
    )
    """


class Captcha:
    """Captcha class"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the captcha class"""
        self.con = con
        self.con.execute(get_captcha_table_creation_query())

    @staticmethod
    def get_random_color() -> Tuple[int, int, int]:
        """Returns a random RGB color as a list"""
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def verify_captcha(self, captcha_id: str, captcha_text: str) -> bool:
        """Verifies if a given captcha is in the database"""
        cur = self.con.cursor()
        query = """
          SELECT
            CaptchaID,
            CaptchaText,
            Expiration
          FROM
            captchas
          WHERE CaptchaID = ? AND CaptchaText = ?
        """
        params = [captcha_id, captcha_text]
        cur.execute(query, params)
        data = cur.fetchone()
        return data is not None

    def delete_old_captchas(self) -> None:
        return

    @staticmethod
    def get_random_border_coordinates() -> Tuple[int, int]:
        """Returns some random coordinates in the border of the image"""
        x = CAPTCHA_WIDTH
        y = CAPTCHA_HEIGHT
        random_boolean = bool(random.getrandbits(1))
        if CAPTCHA_USE_BORDER_LINEAR_RANDOMNESS:
            rand = random.randint(x + y)
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
    def get_captcha_string() -> str:
        """Returns the text used for the captcha"""
        return "".join(random.choice(CAPTCHA_CHARACTERS) for _ in range(CAPTCHA_LENGTH))

    def get_captcha(self, captcha_id: str):
        captcha_text = self.get_captcha_string()
        self.insert_captcha_into_db(captcha_id, captcha_text)
        return captcha_text, self.get_captcha_image(captcha_text)

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
            (captcha_text, captcha_id),
        )
        self.con.commit()
        return

    def delete_captcha(self, captcha_id: str):
        query = """
          DELETE FROM captchas
          WHERE CaptchaID = ?
        """
        self.con.execute(
            query,
            [captcha_id],
        )
        self.con.commit()
        return

    def get_captcha_from_id(self, captcha_id: str) -> Optional[str]:
        """Retrieves the captcha text given a captcha id"""
        cur = self.con.cursor()
        query = """
        SELECT
          CaptchaText
        FROM
          captchas
        WHERE CaptchaID = ?
        """
        row = cur.execute(query, [captcha_id])
        captcha_text = row.fetchone()
        if not captcha_text:
            return None
        return captcha_text[0]

    def get_captcha_image(self, captcha_text: str) -> Image:
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
                x_0 = foo[0]
                y_0 = foo[1]
                foo = self.get_random_border_coordinates()
                x_1 = foo[0]
                y_1 = foo[1]
            else:
                x_0 = random.randint(0, CAPTCHA_WIDTH)
                y_0 = random.randint(0, CAPTCHA_HEIGHT)
                x_1 = random.randint(0, CAPTCHA_WIDTH)
                y_1 = random.randint(0, CAPTCHA_HEIGHT)
            draw = ImageDraw.Draw(image)
            if CAPTCHA_RANDOMIZE_LINES_COLORS:
                lines_color = self.get_random_color()
            draw.line((x_0, y_0, x_1, y_1), fill=lines_color, width=CAPTCHA_LINE_WIDTH)
        return image
