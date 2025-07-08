import re

from src.aibot.env import DB_NAME


class BaseDAO:
    """Base Data Access Object class providing common functionality for database operations."""

    DB_NAME: str = DB_NAME

    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Only letters, numbers, and underscores are allowed."""
        pattern = r"^[A-Za-z0-9_]+$"
        return bool(re.match(pattern, table_name))
