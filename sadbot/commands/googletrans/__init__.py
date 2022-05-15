# pylint: skip-file
"""Free Google Translate API for Python. Translates totally free of charge."""
__all__ = ("Translator",)
__version__ = "4.0.0-rc1"


from sadbot.commands.googletrans.client import Translator
from sadbot.commands.googletrans.constants import LANGCODES, LANGUAGES  # noqa
