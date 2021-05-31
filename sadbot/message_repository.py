"""Here is the MessageRepository class"""

import re
import sqlite3
from typing import Optional, List

from sadbot.config import FBI_WORDS
from sadbot.message import Message


def _create_func(x_val, y_val) -> int:
    """Lambda function for the regex query"""
    return 1 if re.search(x_val, y_val) else 0


def get_table_creation_query() -> str:
    """Returns the table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS messages (
      MessageID        integer,
      SenderName       text,
      SenderID         int,
      ChatID           integer,
      Message          text,
      ReplyToMessageID int
    )"""


def fbi_table_creation_query() -> List[str]:
    """Return a list of queries"""
    query_list = ["""
    CREATE TABLE IF NOT EXISTS fbi_words (
      ID         integer PRIMARY KEY,
      Word       TEXT
    );"""]

    for i in FBI_WORDS:
        word_query = f"INSERT INTO fbi_words (Word) VALUES ('{i}')"
        query_list.append(word_query)

    query_list.append("""
      CREATE TABLE IF NOT EXISTS fbi_entries (
        SenderID     integer,
        ChatID       integer,
        WordID       integer,
        Count        integer
      )
    """)
    return query_list


class MessageRepository:
    """This class handles the messages database"""

    def __init__(self) -> None:
        """Initializes the message repository class"""
        self.con = sqlite3.connect("./messages.db")
        self.con.create_function("regexp", 2, _create_func)
        self.con.execute(get_table_creation_query())
        for query in fbi_table_creation_query():
            self.con.execute(query)

    def insert_message(self, message: Message) -> None:
        """Inserts a message into the database"""
        query = """
          INSERT INTO messages (
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID
          ) VALUES (?, ?, ?, ?, ?, ?)
        """
        self.con.execute(
            query,
            (
                message.id,
                message.sender_name,
                message.sender_id,
                message.chat_id,
                message.text,
                message.reply_id,
            ),
        )
        self.con.commit()

    def get_previous_message(self, message: Message, reg: str) -> Optional[Message]:
        """Retrieves a previous message from the database matching a certain
        regex pattern
        """
        cur = self.con.cursor()
        query = """
          SELECT
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID
          FROM messages
          WHERE Message REGEXP ? AND ChatID = ?
        """
        params = [reg, message.chat_id]
        if message.reply_id:
            query += "AND MessageID = ? "
            params.append(message.reply_id)
        query += "ORDER BY MessageID DESC"
        cur.execute(query, params)
        data = cur.fetchone()
        if data is not None:
            return Message(*data)
        return None

    def get_reply_message(self, message: Message) -> Optional[Message]:
        """Retrieve the reply to a message from DB"""
        cur = self.con.cursor()
        query = """
          SELECT
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID
          FROM messages
          WHERE MessageID = ? and ChatID = ?
      """
        params = [message.reply_id, message.chat_id]
        cur.execute(query, params)
        data = cur.fetchone()
        if data is not None:
            return Message(*data)
        return None

    def get_fbi_word_id(self, word: str) -> Optional[int]:
        """Retrive the WordID of the word"""
        cur = self.con.cursor()
        query = """
        SELECT ID from fbi_words WHERE Word = ?
      """
        row = cur.execute(query, (word,))
        word_id = row.fetchone()[0]
        return word_id

    def get_fbi_entry(self, message: Message, word: str) -> Optional[str]:
        """Retrieve an entry from the DB
        or None if there's no entry with that info"""
        word_id = self.get_fbi_word_id(word)
        query = """
        SELECT * FROM fbi_entries 
        WHERE SenderID = ? and ChatID = ? and WordID = ?
      """
        cur = self.con.cursor()
        cur.execute(query, (message.sender_id, message.chat_id, word_id))
        return cur.fetchone()

    def insert_fbi_entry(self, message: Message, word: str) -> None:
        """Insert an entry into the database"""
        query = """
        INSERT INTO fbi_entries VALUES (?, ?, ?, ?)
        """
        word_id = self.get_fbi_word_id(word)
        cur = self.con.cursor()
        cur.execute(query, (message.sender_id, message.chat_id, word_id, 1))
        self.con.commit()
        return None

    def update_fbi_entry(self, message: Message, word: str) -> None:
        """Update the count of an entry"""
        query = """
        SELECT * from fbi_entries WHERE SenderID = ? and ChatID = ? and WordID = ?
      """
        word_id = self.get_fbi_word_id(word)
        cur = self.con.cursor()
        cur.execute(query, (message.sender_id, message.chat_id, word_id))
        data = cur.fetchone()
        if data is None:
            pass
        count = data[3] + 1
        query = """
        UPDATE fbi_entries SET count = ? WHERE SenderID = ? and ChatID = ? and WordID = ?
      """
        self.con.execute(
            query, (count, message.sender_id, message.chat_id, word_id))
