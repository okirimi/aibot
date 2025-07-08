from src.aibot.cli import logger
from src.aibot.services.system_prompt import SystemPromptService
from src.aibot.yml import CHAT_SYSTEM_DEFAULT


class PromptManager:
    """Manager for handling both dynamic and static system prompts."""

    def __init__(self) -> None:
        """Initialize the PromptManager."""
        self._service: SystemPromptService | None = None
        self._static_prompts: dict[str, str] = {
            "chat": CHAT_SYSTEM_DEFAULT,
        }

    @property
    def service(self) -> "SystemPromptService":
        """Lazy initialization of SystemPromptService to avoid circular imports."""
        if self._service is None:
            self._service = SystemPromptService()
        return self._service

    async def get_chat_system_prompt(self) -> str:
        """Get the system prompt for chat commands.

        Returns
        -------
        str
            The active system prompt or fallback static prompt.
        """
        try:
            # Check if force system mode is enabled
            is_force_enabled = await self.service.is_force_system_enabled()
            if is_force_enabled:
                logger.debug("Force system mode enabled, using default system prompt")
                return self._static_prompts["chat"]

            # Try to get dynamic prompt from database
            active_content = await self.service.get_active_prompt_content()
            if active_content:
                logger.debug("Using dynamic system prompt for chat")
                return active_content  # type: ignore
        except Exception as e:
            logger.warning("Failed to get dynamic prompt, using fallback: %s", e)

        # Fallback to static prompt
        logger.debug("Using static system prompt for chat")
        return self._static_prompts["chat"]

    async def has_active_dynamic_prompt(self) -> bool:
        """Check if there is an active dynamic prompt.

        Returns
        -------
        bool
            True if an active dynamic prompt exists.
        """
        try:
            active_info = await self.service.get_active_prompt_info()
            return active_info is not None
        except Exception as e:
            logger.warning("Failed to check for active prompt: %s", e)
            return False


# Module-level singleton instance
def get_prompt_manager() -> PromptManager:
    """Get the global PromptManager instance.

    Returns
    -------
    PromptManager
        The global PromptManager instance.
    """
    if not hasattr(get_prompt_manager, "instance"):
        get_prompt_manager.instance = PromptManager()  # type: ignore
    return get_prompt_manager.instance  # type: ignore
