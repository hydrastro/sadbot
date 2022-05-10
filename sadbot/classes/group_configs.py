"""Here is the group config class"""
import json
import sqlite3
from typing import Optional, Dict, Any


def get_group_configs_table_creation_query() -> str:
    """Returns the query for creating the user permissions table"""
    return """
      CREATE TABLE IF NOT EXISTS group_configs (
        ChatID       int,
        GroupConfigs text
    )
    """


class GroupConfigs:
    """Group configs class"""

    def __init__(self, con: sqlite3.Connection):
        """Initializes the group configs class"""
        self.con = con
        self.con.execute(get_group_configs_table_creation_query())

    def get_group_config(self, chat_id: int, config_key: str) -> Optional[Any]:
        """Retrieves a group single config"""
        configs = self.get_group_configs(chat_id)
        if configs is None:
            return None
        if config_key in configs:
            return configs[config_key]
        return None

    def set_group_config(self, chat_id: int, config_key: str, config: Any) -> None:
        """Updates a group single config"""
        group_config = self.get_group_configs(chat_id)
        if group_config is None:
            group_config = {}
        group_config.update({config_key: config})
        self.set_group_configs(chat_id, group_config)

    def get_group_configs(self, chat_id: int) -> Optional[Dict]:
        """Retrieves a group whole configs"""
        cur = self.con.cursor()
        query = """
          SELECT
            GroupConfigs
          FROM
             group_configs
          WHERE ChatID = ?
        """
        cur.execute(query, [chat_id])
        data = cur.fetchone()
        if data is None:
            return None
        return json.loads(data[0])

    def set_group_configs(self, chat_id: int, group_config: Dict) -> None:
        """Sets (inserts or updates) a group (whole) config"""
        if self.get_group_configs(chat_id) is not None:
            return self.update_group_configs(chat_id, group_config)
        return self.insert_group_configs(chat_id, group_config)

    def update_group_configs(self, chat_id: int, group_config: Dict) -> None:
        """Updates the group configs"""
        query = """
          UPDATE group_configs
          SET GroupConfigs = ?
          WHERE ChatID = ?
        """
        params = [json.dumps(group_config), chat_id]
        self.con.execute(query, params)
        self.con.commit()

    def insert_group_configs(self, chat_id: int, group_config: Dict) -> None:
        """Inserts the group configs, because they were not yet set"""
        query = """
          INSERT INTO group_configs(
            ChatID,
            GroupConfigs
          ) VALUES (?, ?)
        """
        params = [chat_id, json.dumps(group_config)]
        self.con.execute(query, params)
        self.con.commit()
