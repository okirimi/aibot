import datetime
from pathlib import Path
from typing import Any

from src.aibot.cli import logger
from src.aibot.env import TIMEZONE
from src.aibot.infrastructure.db.dao.prompt_dao import PromptDAO


class SystemPromptService:
    """Service for managing system prompts."""

    def __init__(self) -> None:
        """Initialize the SystemPromptService with a DAO instance."""
        self._dao: PromptDAO = PromptDAO()
        self._prompts_dir: Path = Path("prompts/generated")
        self._ensure_prompts_directory()

    def _ensure_prompts_directory(self) -> None:
        """Ensure the prompts directory exists."""
        try:
            self._prompts_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error("Failed to create prompts directory: %s", e)

    def _generate_filename(self, created_by: int | None = None) -> str | None:
        """Generate a timestamped filename for the prompt file."""
        timestamp = datetime.datetime.now(TIMEZONE)
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

        if created_by:
            return f"prompt_{timestamp_str}_{created_by}.txt"
        logger.warning(
            "No user ID provided for prompt file generation. File generation has been aborted.",
        )
        return None

    def _write_prompt_file(self, file_path: Path, content: str) -> None:
        """Write prompt content to a file."""
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)

    async def create_prompt_from_modal(
        self,
        prompt_content: str,
        created_by: int | None = None,
        *,
        auto_activate: bool = False,
    ) -> dict[str, Any] | None:
        """Create a new system prompt from Modal input."""
        try:
            file_name = self._generate_filename(created_by)
            if not file_name:
                return None

            file_path = self._prompts_dir / file_name

            self._write_prompt_file(file_path, prompt_content.strip())

            # Save to database
            prompt_id = await self._dao.save_prompt(
                prompt=prompt_content.strip(),
                file_path=str(file_path),
                created_by=created_by,
            )

            # Auto-activate if requested
            if auto_activate:
                await self.activate_prompt(prompt_id)

            logger.info(
                "Created new system prompt (ID: %d) with file: %s",
                prompt_id,
                file_name,
            )
            return {
                "success": True,
                "prompt_id": prompt_id,
                "file_path": str(file_path),
                "file_name": file_name,
                "is_active": auto_activate,
            }

        except Exception as e:
            logger.error("Failed to create prompt from modal: %s", e)
            return None

    async def activate_prompt(self, prompt_id: int) -> bool:
        """Activate a specific prompt and deactivate all others."""
        success = await self._dao.activate_prompt(prompt_id)
        if not success:
            logger.error("Failed to activate prompt %d.", prompt_id)
            return False
        return True

    async def get_active_prompt_content(self) -> str | None:
        """Get the content of the currently active system prompt.

        Returns
        -------
        Optional[str]
            The active prompt content, or None if no prompt is active.
        """
        try:
            active_prompt = await self._dao.get_active_prompt()
            return active_prompt # type: ignore
        except Exception as e:
            logger.warning("Failed to get active prompt content: %s", e)
            return None

    async def get_active_prompt_info(self) -> dict[str, Any] | None:
        """Get information about the currently active system prompt."""
        try:
            active_prompt = await self._dao.get_active_prompt()
            if active_prompt:
                return {"prompt": active_prompt}
            return None
        except Exception as e:
            logger.warning("Failed to get active prompt info: %s", e)
            return None
