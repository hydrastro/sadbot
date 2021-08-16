"""Here is the MessageRepository class"""

import datetime
import re
import sqlite3
from typing import Optional, List

from sadbot.message import Message


def _create_func(x_val: str, y_val: str) -> int:
    """Lambda function for the regex query"""
    return 1 if re.search(str(x_val), str(y_val)) else 0


def get_messages_table_creation_query() -> str:
    """Returns the table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS messages (
      MessageID        int,
      SenderName       text,
      SenderID         int,
      ChatID           int,
      Message          text,
      ReplyToMessageID int,
      SenderUsername   text,
      IsBot            bool,
      MessageTime      int
    )
    """


def get_usernames_table_creation_query() -> str:
    """Returns the usernames table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS usernames (
      UserID   int,
      Username text
    )
    """


def get_bot_triggers_table_creation_query() -> str:
    """Returns the bot triggers table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS bot_triggers (
      ChatID      int,
      UserID      int,
      MessageTime int
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
        self.con.execute(get_bot_triggers_table_creation_query())

    def delete_old_bot_triggers_logs(self, time: int) -> None:
        """Deletes old bot triggers"""
        query = """
        DELETE FROM bot_triggers
        WHERE MessageTime < ?
        """
        message_time = datetime.datetime.utcnow().timestamp() - time
        self.con.execute(query, [message_time])
        self.con.commit()

    def get_n_timestamp_chat(self, chat_id: int, message_number: int) -> int:
        """Returns the timestamp of the last n message sent in a specific chat"""
        if message_number == 0:
            return 0
        cur = self.con.cursor()
        query = """
        SELECT
          ChatID,
          UserID,
          MessageTime
        FROM bot_triggers
        WHERE ChatID = ?
        ORDER BY MessageTime DESC
        LIMIT ?
        """
        cur.execute(query, [chat_id, message_number])
        data = cur.fetchall()
        if not data:
            return 0
        if len(data) < message_number:
            return 0
        return data[-1][2]

    def get_n_timestamp_user(self, user_id: int, message_number: int) -> int:
        """Returns the timestamp of the last n message sent by a specific user"""
        if message_number == 0:
            return 0
        cur = self.con.cursor()
        query = """
        SELECT
          ChatID,
          UserID,
          MessageTime
        FROM bot_triggers
        WHERE UserID = ?
        ORDER BY MessageTime DESC
        LIMIT ?
        """
        cur.execute(query, [user_id, message_number])
        data = cur.fetchall()
        if not data:
            return 0
        if len(data) < message_number:
            return 0
        return data[-1][2]

    def log_bot_trigger(self, chat_id: int, user_id: int) -> None:
        """logs a bot trigger"""
        query = """
        INSERT INTO bot_triggers (
          ChatID,
          UserID,
          MessageTime
        ) VALUES (?, ?, ?)
        """
        message_time = datetime.datetime.utcnow().timestamp()
        self.con.execute(query, [chat_id, user_id, message_time])
        self.con.commit()

    def get_user_id_from_username(self, username: str) -> Optional[int]:
        """Checks if a username is in the usernames table"""
        cur = self.con.cursor()
        query = """
              SELECT
                UserID
              FROM usernames
              WHERE Username = ?
            """
        cur.execute(query, [username])
        data = cur.fetchone()
        if data is not None:
            return data[0]
        return None

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

    def update_username(self, user_id: int, username: str) -> bool:
        """Updates a username"""
        query = """
          UPDATE usernames
          SET Username = ?
          WHERE UserID = ?
        """
        self.con.execute(query, [user_id, username])
        self.con.commit()
        return True

    def insert_username(self, user_id: int, username: Optional[str]) -> bool:
        """Inserts a username into the usernames table"""
        if username is None:
            return False
        db_username = self.get_username_from_id(user_id)
        if db_username is not None:
            if db_username != username:
                return self.update_username(user_id, username)
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
            ReplyToMessageID,
            SenderUsername,
            IsBot,
            MessageTime
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                message.sender_username,
                message.is_bot,
                message.message_time,
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
            ReplyToMessageID,
            SenderUsername,
            IsBot,
            MessageTime
          FROM messages
          WHERE Message REGEXP ? AND Message IS NOT NULL AND ChatID = ?
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
            ReplyToMessageID,
            SenderUsername,
            IsBot,
            MessageTime
          FROM messages
          WHERE MessageID = ? AND ChatID = ?
        """
        params = [message.reply_id, message.chat_id]
        cur.execute(query, params)
        data = cur.fetchone()
        if data is not None:
            return Message(*data)
        return None

    def get_message_from_id(self, message_id: int) -> Optional[Message]:
        """Retrieve a message from DB"""
        cur = self.con.cursor()
        query = """
          SELECT
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID,
            SenderUsername,
            IsBot,
            MessageTime
          FROM messages
          WHERE MessageID = ?
        """
        cur.execute(query, [message_id])
        data = cur.fetchone()
        if data is not None:
            return Message(*data)
        return None

    def get_user_last_message(self, user_id: int, chat_id: int) -> Optional[Message]:
        """Gets the last message sent by a user in a specific chat"""
        cur = self.con.cursor()
        query = """
          SELECT
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID,
            SenderUsername,
            IsBot,
            MessageTime
          FROM messages
          WHERE SenderID = ? AND ChatID = ?
          ORDER BY MessageTime DESC
          LIMIT 1
        """
        cur.execute(query, [user_id, chat_id])
        data = cur.fetchall()
        if data is not None and data:
            return Message(*data[0])
        return None

    def get_random_message_from_user(
        self, user_id: int, chat_id: int
    ) -> Optional[Message]:
        """Returns a random message sent by a user in a specific chat"""
        cur = self.con.cursor()
        query = """
          SELECT
            MessageID,
            SenderName,
            SenderID,
            ChatID,
            Message,
            ReplyToMessageID,
            SenderUsername,
            IsBot,
            MessageTime
          FROM messages
          WHERE SenderID = ? AND ChatID = ?
          ORDER BY RANDOM()
          LIMIT 1
        """
        cur.execute(query, [user_id, chat_id])
        data = cur.fetchone()
        if data is not None:
            return Message(*data)
        return None

    def get_user_id_from_message_id(self, message_id: int) -> Optional[int]:
        """Returns the user id from a given message id"""
        message = self.get_message_from_id(message_id)
        if message is None:
            return None
        return message.sender_id
