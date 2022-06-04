"""This is the plugins keyboard handler script"""
from typing import List, Dict
import glob
from os.path import dirname, basename, isfile, join
from math import ceil

from sadbot.classes.group_configs import GroupConfigs


class PluginsKeyboard:
    """Plugins keyboard class"""

    def __init__(self, group_configs: GroupConfigs):
        self.commands = []
        for command_name in [
            basename(f)[:-3]
            for f in glob.glob(join(dirname(__file__), "../commands/", "*.py"))
            if isfile(f)
        ]:
            if command_name == "__init__":
                continue
            self.commands.append(command_name)
        self.commands.remove("plugins")
        self.commands.remove("plugins_callback")
        self.commands.sort()
        self.group_configs = group_configs

    def disable_all_plugins(self, chat_id: int) -> None:
        """Disables all plugins of a chat"""
        self.group_configs.set_group_config(chat_id, "disabled_plugins", self.commands)

    def enable_all_plugins(self, chat_id: int) -> None:
        """Enables all plugins of a chat"""
        self.group_configs.set_group_config(chat_id, "disabled_plugins", [])

    def enable_plugin(self, chat_id: int, plugin_name: str) -> bool:
        """Enables a specific plugin in a chat"""
        disabled_plugins = self.group_configs.get_group_config(
            chat_id, "disabled_plugins"
        )
        if not isinstance(disabled_plugins, list):
            return False
        if plugin_name in disabled_plugins:
            disabled_plugins.remove(plugin_name)
        self.group_configs.set_group_config(
            chat_id, "disabled_plugins", disabled_plugins
        )
        return True

    def disable_plugin(self, chat_id: int, plugin_name: str) -> bool:
        """Disables a specific plugin in a chat"""
        disabled_plugins = self.group_configs.get_group_config(
            chat_id, "disabled_plugins"
        )
        if not isinstance(disabled_plugins, list):
            return False
        disabled_plugins.append(plugin_name)
        self.group_configs.set_group_config(
            chat_id, "disabled_plugins", disabled_plugins
        )
        return True

    @staticmethod
    def get_default_disabled_plugins() -> List[str]:
        """Returns the list of the plugins disabled by default"""
        return ["amogus", "bookmark", "close_thread", "cope", "fbi", "install_kde"]

    def set_default_configs(self, chat_id: int) -> None:
        """Sets the default groups configs"""
        self.group_configs.set_group_config(
            chat_id, "disabled_plugins", self.get_default_disabled_plugins()
        )

    def get_keyboard(self, chat_id: int, current_page: int) -> List:
        """Displays the available plugins in a keyboard"""
        keyboard_data: List[List[Dict[str, str]]] = []
        grid = []
        # callback data is so ugly because the api has a limit on its length
        callback_prefix = f"pk.{chat_id}.{current_page}"
        page_columns = 2
        page_rows = 6
        elements_per_page = page_columns * page_rows
        max_pages = ceil(len(self.commands) / elements_per_page)
        disabled_plugins = self.group_configs.get_group_config(
            chat_id, "disabled_plugins"
        )
        if disabled_plugins is None:
            self.set_default_configs(chat_id)
            disabled_plugins = self.get_default_disabled_plugins()
        for i in range(
            (current_page) * elements_per_page,
            min((current_page + 1) * elements_per_page, len(self.commands)),
        ):
            if self.commands[i] in disabled_plugins:
                command_status = "❌"  # red
                command_action = "e"  # enable
            else:
                command_status = "✅"  # green
                command_action = "d"  # disable
            grid.append(
                {
                    "text": self.commands[i].title().replace("_", " "),
                    "callback_data": f"{callback_prefix}.c.{self.commands[i]}.i",
                }
            )
            grid.append(
                {
                    "text": command_status,
                    "callback_data": f"{callback_prefix}.c.{self.commands[i]}.{command_action}",
                }
            )
        keyboard_data = [
            grid[n : n + page_columns * 2]
            for n in range(0, len(grid), page_columns * 2)
        ]
        previous_next_buttons = []
        if current_page != 0:
            previous_next_buttons.append(
                {
                    "text": "Previous",
                    "callback_data": f"{callback_prefix}.p.{current_page - 1}",
                }
            )
        previous_next_buttons.append(
            {
                "text": f"{current_page + 1}/{max_pages}",
                "callback_data": f"{callback_prefix}.p.c",
            }
        )
        if current_page != max_pages - 1:
            previous_next_buttons.append(
                {
                    "text": "Next",
                    "callback_data": f"{callback_prefix}.p.{current_page + 1}",
                },
            )
        keyboard_data.append(previous_next_buttons)
        keyboard_data.append(
            [
                {"text": "Enable all", "callback_data": f"{callback_prefix}.e"},
                {"text": "Disable all", "callback_data": f"{callback_prefix}.d"},
            ]
        )
        return keyboard_data
