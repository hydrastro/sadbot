"""Here is the user warnings class"""
import sqlite3


def get_warn_table_creation_query() -> str:
    """Returns the warn table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS warn_table (
      ChatID     int,
      UserID     int,
      WarnDate   int
    )
    """


class UserWarnings:
    """This class handles the user warnings"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the message repository class"""
        self.con = con
        self.con.execute(get_warn_table_creation_query())

    def insert_new_warn(self, chat_id: int, user_id: int, message_time: int) -> None:
        """Insert a new warn into the database"""
        query = """
        INSERT INTO warn_table (
          ChatID,
          UserID,
          WarnDate
        ) VALUES (?, ?, ?)
        """
        cur = self.con.cursor()
        cur.execute(query, [chat_id, user_id, message_time])

    def get_warns_since_timestamp(
        self, chat_id: int, user_id: int, timestamp: int
    ) -> int:
        """Get the count of warns since timestamp"""
        query = """
        SELECT
          ChatID,
          UserID,
          WarnDate,
          COUNT(*)
        FROM warn_table
        WHERE ChatID = ?
        AND UserID = ?
        AND WarnDate >= ?
        """
        cur = self.con.cursor()
        cur.execute(query, [chat_id, user_id, timestamp])
        data = cur.fetchall()
        if not data:
            return 0
        return data[0][3]
