"""Here is the MessageRepository class"""

import re
import sqlite3
from typing import Optional, List

from sadbot.message import Message


def _create_func(x_val: str, y_val: str) -> int:
    """Lambda function for the regex query"""
    return 1 if re.search(x_val, y_val) else 0


def get_messages_table_creation_query() -> str:
    """Returns the table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS messages (
      MessageID        integer,
      SenderName       text,
      SenderID         int,
      ChatID           integer,
      Message          text,
      ReplyToMessageID int
    )
    """


def get_usernames_table_creation_query() -> str:
    """Returns the usernames table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS usernames (
      UserID int,
      Username text
    )
    """


class MessageRepository:
    """This class handles the messages database"""

    def __init__(self, con: sqlite3.Connection) -> None:
        """Initializes the message repository class"""
        self.con = con
        self.con.create_function("regexp", 2, _create_func)
        self.con.execute(get_messages_table_creation_query())
        self.con.execute(get_usernames_table_creation_query())

    def get_username_from_id(self, user_id: int) -> Optional[List]:
        """Checks if a userid is in the usernames table"""
        cur = self.con.cursor()
        query = """
              SELECT
                UserID,
                Username
              FROM usernames
              WHERE UserID = ?
            """
        cur.execute(query, [user_id])
        data = cur.fetchone()
        return data

    def insert_username(self, user_id: int, username: str) -> bool:
        """Inserts a username into the usernames table"""
        if self.get_username_from_id(user_id) is None:
            return False
        query = """
          INSERT INTO usernames (
            UserID,
            Username
          ) VALUES (?, ?)
        """
        self.con.execute(query, [user_id, username])
        self.con.commit()
        return True

    def insert_message(self, message: Message) -> None:
        """Inserts a message into the database"""
        self.insert_username(message.sender_id, message.sender_username)
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
                message.message_id,
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

    def edit_message(self, message_id: int, message_text: str) -> None:
        """Edits a message in the messages table and updates the events table"""
        query = """
          UPDATE messages
          SET Message = ?
          WHERE MessageID = ?
        """
        params = [message_text, message_id]
        self.con.execute(query, params)
        self.con.commit()

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
          WHERE MessageID = ? AND ChatID = ?
        """
        params = [message.reply_id, message.chat_id]
        cur.execute(query, params)
        data = cur.fetchone()
        if data is not None:
            return Message(*data)
        return None
