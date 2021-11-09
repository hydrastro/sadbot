"""Here is the revolver class"""
from random import shuffle
import sqlite3
from typing import List, Optional
import json

from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.config import REVOLVER_CHAMBERS, REVOLVER_BULLETS


def get_revolvers_table_creation_query() -> str:
    """Returns the bot triggers table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS revolvers (
      ChatID       int,
      Revolver     str,
      BulletNumber int
    )
    """


class Revolver:
    """This is the revolver class"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the revolver class"""
        self.con = con
        self.con.execute(get_revolvers_table_creation_query())

    def update_revolver_data(self, revolver_data: List) -> None:
        """Updates the revolver entry in the db"""
        query = """
          UPDATE revolvers
          SET Revolver = ?
          BulletNumber = ?
          WHERE ChatID = ?
        """
        self.con.execute(query, [revolver_data[1], revolver_data[2], revolver_data[0]])
        self.con.commit()

    def insert_revolver(self, revolver_data: List) -> None:
        """Inserts a new revolver entry in the db"""
        query = """
        INSERT INTO revolvers (
          ChatID,
          Revolver,
          BulletNumber
        ) VALUES (?, ?, ?)
        """
        self.con.execute(
            query, [revolver_data[0], json.dumps(revolver_data[1]), revolver_data[2]]
        )
        self.con.commit()

    def load_revolver_data(self, chat_id: int) -> Optional[List]:
        """Loads a revolver entry from the db, if present"""
        cur = self.con.cursor()
        query = """
          SELECT
            ChatID,
            Revolver,
            BulletNumber
          FROM
             revolvers
          WHERE ChatID = ?
        """
        cur.execute(query, [chat_id])
        data = cur.fetchone()
        if data is None:
            return None
        return json.loads(data)

    def get_default_revolver_data(self, chat_id) -> List:
        """Returns the default revolver entry"""
        revolver = self.get_revolver(REVOLVER_CHAMBERS)
        return [chat_id, self.reload_revolver(revolver, REVOLVER_BULLETS), 0]

    @staticmethod
    def get_revolver(chambers: int) -> List:
        """Returns an empty revolver given it's capacity"""
        return [0] * chambers

    @staticmethod
    def reload_revolver(revolver: List, bullets: int) -> List:
        """Reloads a revolver"""
        for i in range(0, bullets):
            revolver[i] = 1
        shuffle(revolver)
        return revolver

    def get_revolver_data(self, chat_id: int) -> List:
        """Returns the revolver data, if not found inserts a default one and returns it"""
        revolver = self.load_revolver_data(chat_id)
        if revolver is None:
            revolver = self.get_default_revolver_data(chat_id)
            self.insert_revolver(revolver)
        return revolver

    def shoot(self, chat_id: int) -> List[BotAction]:
        """Shoots"""
        revolver_data = self.get_revolver_data(chat_id)
        if len(revolver_data[1] - 1 < revolver_data[2]):
            return self.exit_message("No more bullets, you have to .reload")
        self.update_revolver_data([chat_id, revolver_data[1], revolver_data[2] + 1])
        if revolver_data[1][revolver_data[2]] == 1:
            return self.exit_message("OH SHIIii.. you're dead, lol.")
        return self.exit_message("Eh.. you survived.")

    def reload(self, chat_id: int, bullets: int) -> List[BotAction]:
        """Reloads"""
        if bullets <= 0:
            return self.exit_message("Invalid inputs.")
        revolver_data = self.get_revolver_data(chat_id)
        if len(revolver_data[1]) <= bullets:
            return self.exit_message(
                "There are too many bullets, y'all would be dead lmao"
            )
        revolver_data = [chat_id, self.reload_revolver(revolver_data[1], bullets), 0]
        self.update_revolver_data(revolver_data)
        return self.exit_message("Reloaded!")

    def revolver(self, chat_id: int, chambers: int, bullets: int) -> List[BotAction]:
        """Changes revolver"""
        if bullets <= 0 or chambers <= 0:
            return self.exit_message("Invalid inputs.")
        self.get_revolver_data(chat_id)
        if bullets >= chambers:
            return self.exit_message("Well, it ain't fun if everybody dies.")
        revolver = self.reload_revolver(self.get_revolver(chambers), bullets)
        self.update_revolver_data([chat_id, revolver, 0])
        return self.exit_message("Changed revolver!")

    @staticmethod
    def exit_message(reply_text: str) -> List[BotAction]:
        """Returns an exit message"""
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
