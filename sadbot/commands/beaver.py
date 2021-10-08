"""Beaver bot command"""

from typing import Optional, List
import re
import sqlite3

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT
from sadbot.functions import safe_cast


class BeaverBotCommand(CommandInterface):
    """This is the beaver bot command class"""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.execute(self.get_beaver_table_creation_query())

    @staticmethod
    def get_beaver_table_creation_query() -> str:
        """Returns the beaver table creation query"""
        return """
        CREATE TABLE IF NOT EXISTS beaver (
          QuoteID   int,
          QuoteText text
        )
        """

    def get_beaver_quote(self, quote_id: Optional[int]) -> Optional[List]:
        """Returns a beaver quote"""
        cur = self.con.cursor()
        query = """
        SELECT
          QuoteID,
          QuoteText
        FROM beaver
        """
        params = []
        if quote_id is None:
            query += "ORDER BY RANDOM()"
        else:
            query += "WHERE QuoteID = ?"
            params.append(quote_id)
        cur.execute(query, params)
        data = cur.fetchone()
        return data

    def get_quote_max_id(self) -> int:
        """Returns the max id (count) of the current quote"""
        cur = self.con.cursor()
        query = """
        SELECT
          QuoteID
        FROM beaver
        ORDER BY QuoteID DESC
        """
        cur.execute(query)
        data = cur.fetchone()
        if data is None:
            return -1
        return data[0]

    def insert_beaver_quote(self, message: Message) -> None:
        """Inserts a beaver quote into the database"""
        if message.text is None:
            return
        query = """
        INSERT INTO beaver(
          QuoteText
        ) VALUES (?)
        """
        quote_id = self.get_quote_max_id() + 1
        self.con.execute(query, [quote_id, message.text])
        self.con.commit()

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching the beaver command"""
        return r".*"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Speaks the truth"""
        if message is None:
            return None
        beaver_user_id = 1749391268
        if message.sender_id == beaver_user_id:
            self.insert_beaver_quote(message)
        command_regex = re.compile(
            r"(!|\.)([Ss][Ee]{2}[Tt][Hh][Ee]|[Bb][Ee][Aa][Vv][Ee][Rr]).*"
        )
        if message.text is None or not re.fullmatch(command_regex, message.text):
            return None
        int_quote_id = None
        split = message.text.split()
        if len(split) > 1:
            quote_id = split[1]
            int_quote_id = safe_cast(quote_id, int, None)
        beaver_quote = self.get_beaver_quote(int_quote_id)
        if beaver_quote is None:
            return None
        beaver_quote_id = beaver_quote[0]
        beaver_quote_text = beaver_quote[1]
        reply_text = (
            f"Here's a quote ({beaver_quote_id}) from beaver:\n{beaver_quote_text}"
        )
        return [BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=reply_text)]
