import datetime

import aiosqlite

from src.suisei.env import TIMEZONE
from src.suisei.infrastructure.db.dao._base import BaseDAO


class AccessLevelDAO(BaseDAO):
    """Data Access Object for managing user access levels.

    Attributes
    ----------
    _table_name : str
        Name of the database table for access levels.
    """

    _table_name: str = "access_level"

    async def create_table(self) -> None:
        """Create table if it doesn't exist.

        Raises
        ------
        ValueError
            If the table name contains invalid characters.
        """
        if not self.validate_table_name(self._table_name):
            msg = "Invalid tablename: Only alphanumeric characters and underscores are allowed."
            raise ValueError(msg)

        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                access_level     TEXT_NOT_NULL,
                enabled_at       DATE NOT NULL,
                disabled_at      DATE DEFAULT NULL
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def enable(self, user_id: int, access_level: str) -> None:
        """Enable a new access level for a user.

        Parameters
        ----------
        user_id : int
            The ID of the user to enable the access level for.
        access_level : str
            The access level to enable.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        date = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            INSERT INTO access_level (user_id, access_level, enabled_at)
            VALUES (?, ?, ?);
            """
            await conn.execute(query, (user_id, access_level, date))
            await conn.commit()
        finally:
            await conn.close()

    async def fetch_user_ids_by_access_level(self, access_level: str) -> list[int]:
        """Fetch IDs of users who have a specific access level.

        Parameters
        ----------
        access_level : str
            The access level to filter by.

        Returns
        -------
        list[int]
            A list of user IDs that have the specified access level.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT user_id FROM access_level WHERE access_level = ?
            AND disabled_at IS NULL;
            """
            cursor = await conn.execute(query, (access_level,))
            result = await cursor.fetchall()
            return [row[0] for row in result]
        finally:
            await conn.close()

    async def disable(self, user_id: int, access_level: str) -> None:
        """Disable an existing access level for a user.

        Parameters
        ----------
        user_id : int
            The ID of the user to disable the access level for.
        access_level : str
            The access level to disable.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        date = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            UPDATE access_level SET disabled_at = ? WHERE user_id = ?
            AND access_level = ?;
            """
            await conn.execute(query, (date, user_id, access_level))
            await conn.commit()
        finally:
            await conn.close()
