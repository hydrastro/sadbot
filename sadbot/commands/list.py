"""List bot command"""
import sqlite3
from typing import Optional, List, Tuple

from sadbot.command_interface import CommandInterface, BOT_HANDLER_TYPE_MESSAGE
from sadbot.message import Message
from sadbot.bot_action import (
    BotAction,
    BOT_ACTION_TYPE_REPLY_TEXT,
    BOT_ACTION_TYPE_NONE,
)


def get_lists_table_creation_query() -> str:
    """Returns the list table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS lists (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Name text,
        ChatID INTEGER
    )
    """


def get_list_entries_table_creation_query() -> str:
    """Returns the entries creation query"""
    return """
    CREATE TABLE IF NOT EXISTS list_entries (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Link text,
        ListID INTEGER
    )
    """


class ListBotCommand(CommandInterface):
    """This is the list bot command class"""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.execute(get_list_entries_table_creation_query())
        self.con.execute(get_lists_table_creation_query())

    @property
    def handler_type(self) -> int:
        """Returns the type of event handled by the command"""
        return BOT_HANDLER_TYPE_MESSAGE

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching letsdo commands"""
        return r"((!|\.)([Ll][Ii][Ss][Tt]\s+.*))"

    def get_reply(self, message: Optional[Message] = None) -> Optional[List[BotAction]]:
        """Returns reply for list command"""
        if message is None or message.text is None:
            return None
        frags = message.text.split(" ")
        if len(frags) == 1:
            action = BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Not enough arguments."
            )
        elif frags[1] == "create":
            action = self.create_list(message)
        elif frags[1] == "add":
            action = self.add_to_list(message)
        elif frags[1] == "remove":
            action = self.remove_from_list(message)
        elif len(frags) == 2:
            action = self.reveal_elements(message)
        else:
            action = BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=f"There is no subcommand for {frags[1]}.",
            )

        return [action]

    def create_list(self, message: Message) -> BotAction:
        """Create a new list with a name"""
        if message.text is None:
            return BotAction(BOT_ACTION_TYPE_NONE)
        frags = message.text.split(" ")
        if len(frags) != 3:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Not enough arguments."
            )
        if self.get_list(frags[2], message.chat_id) is not None:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=f"A list with the name `{frags[2]}` already exists.",
            )
        chat_id = int(str(message.chat_id)[3:])
        self.create_new_list(frags[2], chat_id)
        return BotAction(
            BOT_ACTION_TYPE_REPLY_TEXT, reply_text=f"List `{frags[2]}` was created."
        )

    def add_to_list(self, message: Message) -> BotAction:
        """
        Add a new entry to the list.
        It checks if the link was already added.
        """
        if message.reply_id is None:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text="You must reply to a message in order to add it to the list.",
            )
        if message.text is None:
            return BotAction(BOT_ACTION_TYPE_NONE)
        frags = message.text.split(" ")
        if len(frags) != 3:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Not enough arguments."
            )
        chat_id = int(str(message.chat_id)[3:])
        link_list = self.get_list(frags[2], chat_id)
        if link_list is None:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text="List doesn't exist. First create it.",
            )
        link = f"https://t.me/c/{chat_id}/{message.reply_id}"
        list_id = link_list[0]
        if self.check_existence(link, list_id):
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=f"List {link} is already in the list.",
            )
        self.insert_in_list(link, list_id)
        return BotAction(
            BOT_ACTION_TYPE_REPLY_TEXT,
            reply_text=f"Link {link} was added to list `{frags[2]}`.",
        )

    def remove_from_list(self, message: Message) -> BotAction:
        """Removes an entry from a list"""
        if message.reply_id is None:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text="You must reply to a message in order to remove it from the list.",
            )
        if message.text is None:
            return BotAction(BOT_ACTION_TYPE_NONE)
        frags = message.text.split(" ")
        if len(frags) != 3:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text="Not enough arguments."
            )
        chat_id = int(str(message.chat_id)[3:])
        link_list = self.get_list(frags[2], chat_id)
        if link_list is None:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text="List doesn't exist. First create it.",
            )
        link = f"https://t.me/c/{chat_id}/{message.reply_id}"
        self.remove_entry(link, link_list[0])
        return BotAction(
            BOT_ACTION_TYPE_REPLY_TEXT,
            reply_text=f"Link {link} was removed from list `{frags[2]}`.",
        )

    def reveal_elements(self, message: Message) -> BotAction:
        """Reveals all the entries of a list"""
        if message.text is None:
            return BotAction(BOT_ACTION_TYPE_NONE)
        frags = message.text.split(" ")
        chat_id = int(str(message.chat_id)[3:])
        link_list = self.get_list(frags[1], chat_id)
        if link_list is None:
            return BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT, reply_text=f"List {frags[1]} does not exist"
            )
        entries = self.get_entries(link_list[0])
        mes = f"Entries of list `{frags[1]}`:\n"
        for entry in entries:
            mes += f"{entry}\n"
        mes += "\n"
        return BotAction(BOT_ACTION_TYPE_REPLY_TEXT, reply_text=mes)

    def create_new_list(self, name: str, chat_id: int):
        """Creates a new list in the DB"""
        query = """
        INSERT INTO lists (
            Name,
            ChatID
        ) VALUES (?, ?)
        """
        cur = self.con.cursor()
        cur.execute(query, (name, chat_id))

    def get_list(self, name: str, chat_id: int) -> Optional[Tuple[int, str, int]]:
        """Gets a list from the DB"""
        query = """
        SELECT * FROM lists WHERE Name = ? AND ChatID = ?
        """
        cur = self.con.cursor()
        cur.execute(query, (name, chat_id))
        return cur.fetchone()

    def insert_in_list(self, link: str, list_id: int):
        """Insert a new entry in the DB"""
        query = """
        INSERT INTO list_entries (
            Link,
            ListID
        ) VALUES (?, ?)
        """
        cur = self.con.cursor()
        cur.execute(query, (link, list_id))

    def remove_entry(self, link: str, list_id: int):
        """Remove an entry from the DB"""
        query = """
        DELETE FROM list_entries
        WHERE Link = ?
        AND ListID = ?
        """
        cur = self.con.cursor()
        cur.execute(query, (link, list_id))

    def get_entries(self, list_id: int) -> List[str]:
        """Get all the entries of a list"""
        query = """
        SELECT
        Link FROM list_entries
        WHERE ListID = ?
        """
        cur = self.con.cursor()
        cur.execute(query, [list_id])
        entries = []
        for entry in cur.fetchall():
            entries.append(entry[0])
        return entries

    def check_existence(self, link: str, list_id: int) -> bool:
        """Checks if a link is already present in the entries"""
        query = """
        SELECT * FROM list_entries
        WHERE ListID = ?
        AND Link = ?
        """
        cur = self.con.cursor()
        cur.execute(query, (list_id, link))
        return cur.fetchone() is not None
