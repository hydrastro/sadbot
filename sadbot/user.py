"""User dataclass"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User dataclass"""

    user_id: int
    user_username: Optional[str]
