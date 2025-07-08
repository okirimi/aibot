import datetime
from typing import Any

import aiosqlite

from src.aibot.cli import logger
from src.aibot.env import TIMEZONE
from src.aibot.infrastructure.db.dao.base import BaseDAO


class PromptDAO(BaseDAO):
    """Data Access Object for managing system prompts.

    Attributes
    ----------
    _table_name : str
        Name of the database table for system prompts.
    """

    _table_name: str = "system_prompt"

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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                activated_at DATETIME DEFAULT NULL,
                deactivated_at DATETIME DEFAULT NULL,
                is_active BOOLEAN DEFAULT FALSE
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def save_prompt(
        self,
        prompt: str,
        file_path: str,
        created_by: int,
    ) -> int | None:
        """Save a new system prompt to the database.

        Parameters
        ----------
        prompt : str
            The system prompt content.
        file_path : str
            Path to the generated prompt file.
        created_by : int
            User ID who created this prompt.

        Returns
        -------
        int
            The ID of the newly created prompt.
        """
        if not prompt or not prompt.strip():
            msg = "Prompt content cannot be empty."
            logger.warning(msg)

        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            INSERT INTO system_prompt (prompt, file_path, created_by)
            VALUES (?, ?, ?);
            """
            cursor = await conn.execute(query, (prompt.strip(), file_path, created_by))
            await conn.commit()
            if cursor.lastrowid is None:
                msg = "Failed to create prompt: no ID returned"
                logger.error(msg)
            return cursor.lastrowid
        finally:
            await conn.close()

    async def get_prompt_row_by_id(self, prompt_id: int) -> dict[str, Any] | None:
        """Get a complete prompt row by its ID.

        Parameters
        ----------
        prompt_id : int
            The ID of the prompt to retrieve.

        Returns
        -------
        dict[str, any] | None
            Dictionary containing complete prompt row data if found, None otherwise.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT id, prompt, file_path, created_by, created_at,
                   activated_at, deactivated_at, is_active
            FROM system_prompt
            WHERE id = ?;
            """
            cursor = await conn.execute(query, (prompt_id,))
            row = await cursor.fetchone()

            if row:
                return {
                    "id": row[0],
                    "prompt": row[1],
                    "file_path": row[2],
                    "created_by": row[3],
                    "created_at": row[4],
                    "activated_at": row[5],
                    "deactivated_at": row[6],
                    "is_active": bool(row[7]),
                }
            return None
        finally:
            await conn.close()

    async def get_active_prompt(self) -> str | None:
        """Get the prompt text from the currently active prompt.

        Returns
        -------
        str | None
            The prompt text if an active prompt exists with non-null activated_at and
            is_active=True, None otherwise.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT prompt
            FROM system_prompt
            WHERE activated_at IS NOT NULL AND is_active = TRUE
            ORDER BY activated_at DESC
            LIMIT 1;
            """
            cursor = await conn.execute(query)
            row = await cursor.fetchone()

            return row[0] if row else None
        finally:
            await conn.close()

    async def _deactivate_all_prompts(self) -> int:
        """Deactivate all currently active prompts.

        Returns
        -------
        int
            Number of prompts that were deactivated.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        deactivated_at = datetime.datetime.now(TIMEZONE)

        try:
            query = """
            UPDATE system_prompt
            SET is_active = FALSE, deactivated_at = ?
            WHERE is_active = TRUE;
            """
            cursor = await conn.execute(query, (deactivated_at,))
            await conn.commit()
            return cursor.rowcount or 0
        finally:
            await conn.close()

    async def activate_prompt(self, prompt_id: int) -> bool:
        """Activate a specific prompt and deactivate all others.

        Parameters
        ----------
        prompt_id : int
            The ID of the prompt to activate.

        Returns
        -------
        bool
            True if the prompt was successfully activated, False otherwise.
        """
        # First deactivate all prompts
        await self._deactivate_all_prompts()

        # Then activate the specified prompt
        conn = await aiosqlite.connect(super().DB_NAME)
        activated_at = datetime.datetime.now(TIMEZONE)

        try:
            query = """
            UPDATE system_prompt
            SET is_active = TRUE, activated_at = ?, deactivated_at = NULL
            WHERE id = ?;
            """
            cursor = await conn.execute(query, (activated_at, prompt_id))
            await conn.commit()

            return cursor.rowcount > 0
        finally:
            await conn.close()
