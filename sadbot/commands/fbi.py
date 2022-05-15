"""FBI bot command"""

import sqlite3
from typing import Optional, List
import re

from sadbot.config import FBI_WORDS, FBI_MOST_WANTED_NUMBER
from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


def fbi_words_table_creation_query() -> str:
    """Returns the FBI words table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS fbi_words (
      ID   integer PRIMARY KEY,
      Word TEXT
    )"""


def fbi_entries_table_creation_query() -> str:
    """Returns the FBI entries table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS fbi_entries (
      SenderID integer,
      ChatID   integer,
      WordID   integer,
      Count    integer
    )
    """


class FbiBotCommand(CommandInterface):
    """This is the FBI bot command class"""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.execute(fbi_words_table_creation_query())
        self.con.execute(fbi_entries_table_creation_query())
        self.initialize_forbidden_words()

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching 4channel commands"""
        return r".*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Doesn't really return a reply, just monitors words"""
        if message is None or message.text is None:
            return None
        forbidden_words = []
        for word in FBI_WORDS:
            if word in message.text.lower():
                forbidden_words.append(word)
        for word in forbidden_words:
            data = self.get_fbi_entry(message, word)
            if data is None:
                self.insert_fbi_entry(message, word)
                return None
            self.update_fbi_entry(message, word)
        if re.fullmatch(
            re.compile(r"(\.|!)[Ww][Aa][Tt][Cc][Hh][Ll][Ii][Ss][Tt].*"), message.text
        ):
            reply_text = f"Top {FBI_MOST_WANTED_NUMBER} most wanted:"
            # word = None
            # if len(message.text) > 14:
            #    word = message.text[14:]
            count = FBI_MOST_WANTED_NUMBER
            for criminal in self.get_most_wanted(count, message.chat_id):
                reply_text += f"\n{criminal[2]} - {criminal[1]}"
            return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
        return None

    def initialize_forbidden_words(self):
        """Initializes the forbidden words table, inserting new words it there are any"""
        cur = self.con.cursor()
        for forbidden_word in FBI_WORDS:
            if self.get_fbi_word_id(forbidden_word) is None:
                cur.execute("INSERT INTO fbi_words (Word) VALUES (?)", [forbidden_word])
                self.con.commit()

    def get_fbi_word_id(self, word: str) -> Optional[int]:
        """Retrieves the WordID of the word"""
        cur = self.con.cursor()
        query = """
          SELECT
            ID
          FROM fbi_words
          WHERE Word = ?
        """
        row = cur.execute(query, (word,))
        word_id = row.fetchone()
        if not word_id:
            return None
        return word_id[0]

    def get_fbi_entry(self, message: Message, word: str) -> Optional[str]:
        """Retrieves an entry from the DB or None if there's no entry with that info"""
        word_id = self.get_fbi_word_id(word)
        query = """
          SELECT
            SenderID,
            ChatID,
            WordID,
            Count
          FROM fbi_entries
          WHERE SenderID = ? AND ChatID = ? AND WordID = ?
        """
        cur = self.con.cursor()
        cur.execute(query, (message.sender_id, message.chat_id, word_id))
        return cur.fetchone()

    def get_most_wanted(self, list_length: int, chat_id: int) -> List:
        """Returns the most wanted list"""
        query = """
          SELECT
            SenderID,
            SUM(Count) as foo,
            usernames.Username
          FROM
            fbi_entries
          JOIN usernames
          ON usernames.UserID=fbi_entries.SenderID
          WHERE ChatID = ?
          GROUP BY SenderID
          ORDER BY foo DESC
          LIMIT ?
        """
        cur = self.con.cursor()
        cur.execute(query, [chat_id, list_length])
        return cur.fetchall()

    def insert_fbi_entry(self, message: Message, word: str) -> None:
        """Insert an entry into the database"""
        query = """
          INSERT INTO fbi_entries (
            SenderID,
            ChatID,
            WordID,
            Count
          )  VALUES (?, ?, ?, ?)
        """
        word_id = self.get_fbi_word_id(word)
        cur = self.con.cursor()
        cur.execute(query, (message.sender_id, message.chat_id, word_id, 1))
        self.con.commit()

    def update_fbi_entry(self, message: Message, word: str) -> None:
        """Updates the count of an entry"""
        query = """
          SELECT
            SenderID,
            ChatID,
            WordID,
            Count
          FROM fbi_entries
          WHERE SenderID = ? AND ChatID = ? AND WordID = ?
        """
        word_id = self.get_fbi_word_id(word)
        cur = self.con.cursor()
        cur.execute(query, (message.sender_id, message.chat_id, word_id))
        data = cur.fetchone()
        if data is None:
            pass
        count = data[3] + 1
        query = """
          UPDATE fbi_entries
          SET count = ?
          WHERE SenderID = ? AND ChatID = ? AND WordID = ?"""
        self.con.execute(query, (count, message.sender_id, message.chat_id, word_id))
