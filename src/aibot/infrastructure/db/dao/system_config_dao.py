import aiosqlite

from src.aibot.infrastructure.db.dao.base import BaseDAO


class SystemConfigDAO(BaseDAO):
    """Data Access Object for managing system configuration.

    Attributes
    ----------
    _table_name : str
        Name of the database table for system configuration.
    """

    _table_name: str = "system_config"

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
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def set_config(self, key: str, value: str) -> bool:
        """Set a configuration value.

        Parameters
        ----------
        key : str
            Configuration key.
        value : str
            Configuration value.

        Returns
        -------
        bool
            True if the configuration was successfully set, False otherwise.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            INSERT OR REPLACE INTO system_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP);
            """
            cursor = await conn.execute(query, (key, value))
            await conn.commit()
            return cursor.rowcount > 0
        finally:
            await conn.close()

    async def get_config(self, key: str, default: str | None = None) -> str | None:
        """Get a configuration value.

        Parameters
        ----------
        key : str
            Configuration key.
        default : str | None
            Default value to return if key not found.

        Returns
        -------
        str | None
            The configuration value if found, default value otherwise.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT value FROM system_config WHERE key = ?;
            """
            cursor = await conn.execute(query, (key,))
            row = await cursor.fetchone()
            return row[0] if row else default
        finally:
            await conn.close()

    async def delete_config(self, key: str) -> bool:
        """Delete a configuration value.

        Parameters
        ----------
        key : str
            Configuration key to delete.

        Returns
        -------
        bool
            True if the configuration was successfully deleted, False otherwise.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            DELETE FROM system_config WHERE key = ?;
            """
            cursor = await conn.execute(query, (key,))
            await conn.commit()
            return cursor.rowcount > 0
        finally:
            await conn.close()

    async def is_force_system_enabled(self) -> bool:
        """Check if force system mode is enabled.

        Returns
        -------
        bool
            True if force system mode is enabled, False otherwise.
        """
        value = await self.get_config("force_system_mode", "false")
        return (value or "false").lower() == "true"

    async def enable_force_system(self) -> bool:
        """Enable force system mode.

        Returns
        -------
        bool
            True if successfully enabled, False otherwise.
        """
        return await self.set_config("force_system_mode", "true")

    async def disable_force_system(self) -> bool:
        """Disable force system mode.

        Returns
        -------
        bool
            True if successfully disabled, False otherwise.
        """
        return await self.set_config("force_system_mode", "false")
