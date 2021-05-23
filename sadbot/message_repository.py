"""Here is the MessageRepository class"""

import re
import sqlite3
from typing import Optional

from sadbot.message import Message


def _create_func(x_val, y_val) -> int:
    """Lambda function for the regex query"""
    return 1 if re.search(x_val, y_val) else 0


class MessageRepository:
    """This class handles the messages database"""

    def __init__(self) -> None:
        """Initializes the message repository class"""
        self.con = sqlite3.connect("./messages.db")
        self.con.create_function("regexp", 2, _create_func)
        self.con.execute(self.get_table_creation_query())

    def get_table_creation_query(self) -> str:
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
