import re
from pathlib import Path
from typing import Any

from src.aibot.cli import logger
from src.aibot.infrastructure.db.dao.prompt_dao import PromptDAO
from src.aibot.infrastructure.db.dao.system_config_dao import SystemConfigDAO
from src.aibot.yml import CHAT_SYSTEM_DEFAULT


class SystemPromptService:
    """Service for managing system prompts."""

    def __init__(self) -> None:
        """Initialize the SystemPromptService with a DAO instance."""
        self._dao: PromptDAO = PromptDAO()
        self._config_dao: SystemConfigDAO = SystemConfigDAO()
        self._prompts_dir: Path = Path("resources/generated")
        self._ensure_prompts_directory()

    def _ensure_prompts_directory(self) -> None:
        """Ensure the prompts directory exists."""
        try:
            self._prompts_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error("Failed to create prompts directory: %s", e)

    def _get_existing_file_numbers(self) -> list[int]:
        """Get list of existing file numbers from chat_sys_xx.txt files.

        Returns
        -------
        list[int]
            Sorted list of existing file numbers.
        """
        pattern = re.compile(r"^chat_sys_(\d+)\.txt$")
        numbers = []

        for file_path in self._prompts_dir.glob("chat_sys_*.txt"):
            match = pattern.match(file_path.name)
            if match:
                numbers.append(int(match.group(1)))

        return sorted(numbers)

    def _shift_existing_files(self) -> None:
        """Shift existing files up by one number (0->1, 1->2, etc.).

        Files with number 99 and above will be deleted along with their DB records.
        """
        existing_numbers = self._get_existing_file_numbers()

        # Process in reverse order to avoid conflicts
        for number in reversed(existing_numbers):
            old_path = self._prompts_dir / f"chat_sys_{number}.txt"

            if number >= 99:  # noqa:PLR2004
                # Delete file and DB record for numbers >= 99
                self._delete_file_and_db_record(old_path)
            else:
                # Shift to next number
                new_path = self._prompts_dir / f"chat_sys_{number + 1}.txt"
                try:
                    old_path.rename(new_path)
                    # Update DB record with new file path
                    self._update_file_path_in_db(str(old_path), str(new_path))
                except OSError as e:
                    logger.error("Failed to rename file %s to %s: %s", old_path, new_path, e)

    def _delete_file_and_db_record(self, file_path: Path) -> None:
        """Delete a file and its corresponding DB record.

        Parameters
        ----------
        file_path : Path
            Path of the file to delete.
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info("Deleted file: %s", file_path)
        except OSError as e:
            logger.error("Failed to delete file %s: %s", file_path, e)

        # Delete from DB asynchronously (we'll need to handle this properly)
        # For now, we'll store the path for later deletion
        self._files_to_delete_from_db = getattr(self, "_files_to_delete_from_db", [])
        self._files_to_delete_from_db.append(str(file_path))

    def _update_file_path_in_db(self, old_path: str, new_path: str) -> None:
        """Update file path in database (placeholder for async operation).

        Parameters
        ----------
        old_path : str
            Old file path.
        new_path : str
            New file path.
        """
        # Store for later async update
        self._path_updates = getattr(self, "_path_updates", [])
        self._path_updates.append((old_path, new_path))

    async def _process_pending_db_operations(self) -> None:
        """Process pending database operations."""
        # Delete files from DB
        if hasattr(self, "_files_to_delete_from_db"):
            for file_path in self._files_to_delete_from_db:
                await self._dao.delete_prompt_by_file_path(file_path)
            delattr(self, "_files_to_delete_from_db")

        # Update file paths in DB
        if hasattr(self, "_path_updates"):
            for old_path, new_path in self._path_updates:
                await self._dao.update_file_path(old_path, new_path)
            delattr(self, "_path_updates")

    def _generate_filename(self, created_by: int | None = None) -> str | None:
        """Generate filename in chat_sys_xx.txt format.

        Parameters
        ----------
        created_by : int | None
            User ID (currently not used in new format).

        Returns
        -------
        str | None
            Generated filename or None if creation failed.
        """
        if created_by is None:
            logger.warning(
                "No user ID provided for file generation. File generation has been aborted.",
            )
            return None

        # Shift existing files up by one number
        self._shift_existing_files()

        # New file always gets number 0
        return "chat_sys_0.txt"

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
            # Process any pending DB operations first
            await self._process_pending_db_operations()

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

            # Process any remaining DB operations from file shifting
            await self._process_pending_db_operations()

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
            return active_prompt  # type: ignore
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

    def get_available_prompt_files(self) -> list[dict[str, Any]]:
        """Get list of available prompt files with preview text.

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing file info and preview text.
        """
        files_info = []
        pattern = re.compile(r"^chat_sys_(\d+)\.txt$")

        for file_path in sorted(self._prompts_dir.glob("chat_sys_*.txt")):
            match = pattern.match(file_path.name)
            if match:
                number = int(match.group(1))
                try:
                    with file_path.open("r", encoding="utf-8") as f:
                        content = f.read().strip()
                        preview = content[:20] if content else "**ファイルが空白です**"
                        if len(content) > 20:  # noqa:PLR2004
                            preview += "..."

                        files_info.append(
                            {
                                "number": number,
                                "filename": file_path.name,
                                "filepath": str(file_path),
                                "preview": preview,
                                "full_content": content,
                            },
                        )
                except Exception as e:
                    logger.warning("Failed to read file %s: %s", file_path, e)

        # Sort by number (0 is newest)
        from typing import cast

        files_info.sort(key=lambda x: cast("int", x["number"]))
        return files_info

    def get_prompt_content_by_number(self, number: int) -> str | None:
        """Get prompt content by file number.

        Parameters
        ----------
        number : int
            The file number (0-99).

        Returns
        -------
        str | None
            The content of the prompt file, or None if not found.
        """
        file_path = self._prompts_dir / f"chat_sys_{number}.txt"

        if not file_path.exists():
            return None

        try:
            with file_path.open("r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logger.warning("Failed to read file %s: %s", file_path, e)
            return None

    async def reactivate_prompt_by_number(
        self,
        number: int,
        created_by: int,
    ) -> dict[str, Any] | None:
        """Reactivate a prompt by file number.

        Parameters
        ----------
        number : int
            The file number (0-99).
        created_by : int
            User ID who is reactivating the prompt.

        Returns
        -------
        dict[str, Any] | None
            Success information or None if failed.
        """
        content = self.get_prompt_content_by_number(number)
        if not content:
            return None

        try:
            # Create new prompt with the content
            result = await self.create_prompt_from_modal(
                prompt_content=content,
                created_by=created_by,
                auto_activate=True,
            )

            if result and result.get("success"):
                logger.info(
                    "Reactivated prompt from chat_sys_%d.txt (new ID: %d) by user %d",
                    number,
                    result["prompt_id"],
                    created_by,
                )
                return {
                    "success": True,
                    "original_number": number,
                    "new_prompt_id": result["prompt_id"],
                    "content": content,
                }
            return None

        except Exception as e:
            logger.error("Failed to reactivate prompt from number %d: %s", number, e)
            return None

    async def enable_force_system_mode(self, admin_user_id: int) -> dict[str, Any]:
        """Enable force system mode with default instructions.

        Parameters
        ----------
        admin_user_id : int
            Admin user ID who is enabling force mode.

        Returns
        -------
        dict[str, Any]
            Result information.
        """
        try:
            # Enable force system mode
            await self._config_dao.enable_force_system()

            # Set default system instructions as active prompt
            result = await self.create_prompt_from_modal(
                prompt_content=CHAT_SYSTEM_DEFAULT,
                created_by=admin_user_id,
                auto_activate=True,
            )

            if result and result.get("success"):
                logger.info(
                    "Force system mode enabled by admin %d with default instructions (ID: %d)",
                    admin_user_id,
                    result["prompt_id"],
                )
                return {
                    "success": True,
                    "message": (
                        "強制システムモードが有効になりました。"
                        "デフォルトのシステム指示が適用されています。"
                    ),
                    "prompt_id": result["prompt_id"],
                }
            # Force mode was enabled but prompt creation failed
            logger.error(
                "Force mode enabled but failed to set default prompt by admin %d",
                admin_user_id,
            )
            return {
                "success": False,
                "message": (
                    "強制システムモードは有効になりましたが、デフォルト指示の設定に失敗しました。"
                ),
            }

        except Exception as e:
            logger.error("Failed to enable force system mode: %s", e)
            return {
                "success": False,
                "message": "強制システムモードの有効化に失敗しました。",
            }

    async def disable_force_system_mode(self, admin_user_id: int) -> dict[str, Any]:
        """Disable force system mode.

        Parameters
        ----------
        admin_user_id : int
            Admin user ID who is disabling force mode.

        Returns
        -------
        dict[str, Any]
            Result information.
        """
        try:
            success = await self._config_dao.disable_force_system()

            if success:
                logger.info("Force system mode disabled by admin %d", admin_user_id)
                return {
                    "success": True,
                    "message": (
                        "強制システムモードが無効になりました。"
                        "ユーザーは自由にシステム指示を設定できます。"
                    ),
                }
            logger.error("Failed to disable force system mode by admin %d", admin_user_id)
            return {
                "success": False,
                "message": "強制システムモードの無効化に失敗しました。",
            }

        except Exception as e:
            logger.error("Failed to disable force system mode: %s", e)
            return {
                "success": False,
                "message": "強制システムモードの無効化に失敗しました。",
            }

    async def reset_to_default_system(self, user_id: int) -> dict[str, Any]:
        """Reset system prompt to default instructions.

        Parameters
        ----------
        user_id : int
            User ID who is resetting to default.

        Returns
        -------
        dict[str, Any]
            Result information.
        """
        try:
            result = await self.create_prompt_from_modal(
                prompt_content=CHAT_SYSTEM_DEFAULT,
                created_by=user_id,
                auto_activate=True,
            )

            if result and result.get("success"):
                logger.info(
                    "System prompt reset to default by user %d (ID: %d)",
                    user_id,
                    result["prompt_id"],
                )
                return {
                    "success": True,
                    "message": "システム指示をデフォルトにリセットしました。",
                    "prompt_id": result["prompt_id"],
                }
            logger.error("Failed to reset system prompt to default by user %d", user_id)
            return {
                "success": False,
                "message": "デフォルトシステム指示の設定に失敗しました。",
            }

        except Exception as e:
            logger.error("Failed to reset system prompt to default: %s", e)
            return {
                "success": False,
                "message": "デフォルトシステム指示の設定に失敗しました。",
            }

    async def is_force_system_enabled(self) -> bool:
        """Check if force system mode is enabled.

        Returns
        -------
        bool
            True if force system mode is enabled, False otherwise.
        """
        return bool(await self._config_dao.is_force_system_enabled())
