"""Here is the reminder manager"""
import datetime
import sqlite3
from typing import Optional, List, Dict

from sadbot.message import Message
from sadbot.message_repository import MessageRepository
from sadbot.action_manager_interface import ActionManagerInterface
from sadbot.bot_action import BotAction, BOT_ACTION_TYPE_REPLY_TEXT


def get_reminders_table_creation_query() -> str:
    """Returns the table creation query"""
    return """
    CREATE TABLE IF NOT EXISTS reminders (
      TriggerMessageID  int,
      RemindMessageID   int,
      RemindUserID      text,
      RemindTime        int
    )
    """


class RemindMeManager(ActionManagerInterface):
    """Handles the reminder"""

    def __init__(
        self,
        con: sqlite3.Connection,
        message_repository: MessageRepository,
    ):
        """Initializes the event handler"""
        self.con = con
        self.con.execute(get_reminders_table_creation_query())
        self.message_repository = message_repository

    def handle_callback(
        self,
        trigger_message: Message,
        sent_message: Optional[Message],
        callback_manager_info: Optional[Dict],
    ) -> None:
        if callback_manager_info is None:
            return
        if "remind_time" in callback_manager_info:
            duration = callback_manager_info["remind_time"]
        self.set_reminder(trigger_message, duration)

    def set_reminder(self, trigger_message: Message, duration: int) -> None:
        """Inserts a reminder into the db"""
        query = """
        INSERT INTO reminders (
          TriggerMessageID,
          RemindMessageID,
          RemindUserID,
          RemindTime
        ) VALUES (?, ?, ?, ?)
        """
        remind_time = datetime.datetime.utcnow().timestamp() + duration
        self.con.execute(
            query,
            [
                trigger_message.message_id,
                trigger_message.reply_id,
                trigger_message.sender_id,
                remind_time,
            ],
        )
        self.con.commit()

    def delete_expired_reminders(self) -> None:
        """Removes expired reminders"""
        query = """
        DELETE FROM reminders
        WHERE RemindTime < ?
        """
        message_time = datetime.datetime.utcnow().timestamp()
        self.con.execute(query, [message_time])
        self.con.commit()

    def get_reminders(self) -> Optional[List]:
        """Gets all the reminders"""
        cur = self.con.cursor()
        query = """
        SELECT
          TriggerMessageID,
          RemindMessageID,
          RemindUserID,
          RemindTime
        FROM reminders
        """
        cur.execute(query)
        return cur.fetchall()

    def get_remind_reply(
        self, trigger_message_id: int, reminder_message_id: int
    ) -> List:
        """Returns the single reminder reply"""
        trigger_message = self.message_repository.get_message_from_id(
            trigger_message_id
        )
        if trigger_message is not None:
            user = (
                f"@{trigger_message.sender_username}"
                if trigger_message.sender_username is not None
                else trigger_message.sender_name
            )
        else:
            user = "user"
        reply_text = f"Yo {user}, you told me to remind you this now:\n"
        remind_message = self.message_repository.get_message_from_id(
            reminder_message_id
        )
        if remind_message is not None and remind_message.text is not None:
            reply_text += remind_message.text
        else:
            reply_text += "I forgor 💀"
        actions = [
            BotAction(
                BOT_ACTION_TYPE_REPLY_TEXT,
                reply_text=reply_text,
                reply_to_message_id=reminder_message_id,
            )
        ]
        return [trigger_message, actions]

    def get_actions(self) -> Optional[List[List]]:
        """This is a wise funcitons which knows stuff and reminds it lol"""
        knowledge = self.get_reminders()
        if knowledge is None:
            return None
        actions = []
        for reminder in knowledge:
            if reminder[3] < datetime.datetime.utcnow().timestamp():
                actions.append(self.get_remind_reply(reminder[0], reminder[1]))
        self.delete_expired_reminders()
        return actions
