"""Here is the user permissions class"""
import json
import sqlite3
import time
from dataclasses import asdict
from typing import Optional

from sadbot.chat_permissions import ChatPermissions


def get_user_permissions_table_creation_query() -> str:
    """Returns the query for creating the user permissions table"""
    return """
    CREATE TABLE IF NOT EXISTS user_permissions (
      UserID           int,
      ChatID           int,
      Permissions      str,
      Expiration       int
    )
    """


class Permissions:
    """Permissions class"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the captcha class"""
        self.con = con
        self.con.execute(get_user_permissions_table_creation_query())

    def get_user_permissions(
        self, user_id: int, chat_id: int
    ) -> Optional[ChatPermissions]:
        """Retrieves existing user permissions from the database, if there are any"""
        cur = self.con.cursor()
        query = """
          SELECT
            Permissions,
            Expiration
          FROM
            user_permissions
          WHERE UserID = ? AND ChatID = ?
        """
        params = [user_id, chat_id]
        cur.execute(query, params)
        data = cur.fetchone()
        if data is None:
            return None
        if time.time() > data[1] != 0:
            self.delete_expired_permissions(user_id, chat_id)
            return None
        return ChatPermissions(**json.loads(data[0]))

    def delete_expired_permissions(self, user_id: int, chat_id: int) -> None:
        """Deletes the expired permissions form the database"""
        query = """
          DELETE FROM
            user_permissions
          WHERE UserID = ? AND ChatID = ?
        """
        self.con.execute(query, (user_id, chat_id))
        self.con.commit()

    def insert_user_permissions(
        self,
        user_id: int,
        chat_id: int,
        permissions: ChatPermissions,
        expiration: Optional[int] = 0,
    ) -> None:
        """Inserts new user permissions in the database"""
        query = """
          INSERT INTO user_permissions (
            UserID,
            ChatID,
            Permissions,
            Expiration
          ) VALUES (?, ?, ?, ?)
        """
        if expiration is None:
            expiration = 0
        string_permissions = json.dumps(asdict(permissions))
        self.con.execute(query, (user_id, chat_id, string_permissions, expiration))
        self.con.commit()

    def update_user_permissions(
        self,
        user_id: int,
        chat_id: int,
        permissions: ChatPermissions,
        expiration: Optional[int] = 0,
    ):
        """Updates existing user permissions in the database"""
        query = """
          UPDATE user_permissions
          SET Permissions = ?, Expiration = ?
          WHERE UserID = ? AND ChatID = ?
        """
        if expiration is None:
            expiration = 0
        string_permissions = json.dumps(asdict(permissions))
        self.con.execute(query, (string_permissions, expiration, user_id, chat_id))
        self.con.commit()

    def set_user_permissions(
        self,
        user_id: int,
        chat_id: int,
        permissions: ChatPermissions,
        expiration: Optional[int] = 0,
    ):
        """Inserts or, if there already are, updates, user permissions in the database"""
        if self.get_user_permissions(user_id, chat_id) is None:
            return self.insert_user_permissions(
                user_id, chat_id, permissions, expiration
            )
        return self.update_user_permissions(user_id, chat_id, permissions, expiration)

    def delete_user_permissions(self, user_id: int, chat_id: int) -> None:
        """Deletes user permissions form the database"""
        query = """
          DELETE FROM user_permissions
          WHERE UserID = ? AND ChatID = ?
        """
        self.con.execute(query, (user_id, chat_id))
        self.con.commit()
