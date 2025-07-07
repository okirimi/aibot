from src.aibot.adapters.chat import ChatMessage
from src.aibot.adapters.response import ResponseResult
from src.aibot.cli import logger
from src.aibot.env import (
    CHAT_MAX_TOKENS,
    CHAT_MODEL,
    CHAT_TEMPERATURE,
    CHAT_TOP_P,
)
from src.aibot.infrastructure.api.anthropic_api import generate_anthropic_response
from src.aibot.infrastructure.api.gemini_api import generate_gemini_response
from src.aibot.infrastructure.api.openai_api import generate_openai_response
from src.aibot.services.provider_manager import ProviderManager, ProviderType
from src.aibot.types import ClaudeParams, GeminiParams, GPTParams, ParamsType


class ApiFactory:
    """Factory class for generating responses from different AI providers."""

    def __init__(self) -> None:
        """Initialize the API factory."""
        self._provider_manager = ProviderManager.get_instance()

    def _create_model_params(self, provider: ProviderType) -> ParamsType:
        """Create model parameters based on the provider type."""
        if provider == "anthropic":
            return ClaudeParams(
                model=CHAT_MODEL,
                max_tokens=CHAT_MAX_TOKENS,
                temperature=CHAT_TEMPERATURE,
                top_p=CHAT_TOP_P,
            )
        elif provider == "google":  # noqa: RET505
            return GeminiParams(
                model=CHAT_MODEL,
                temperature=CHAT_TEMPERATURE,
                top_p=CHAT_TOP_P,
            )
        elif provider == "openai":
            return GPTParams(
                model=CHAT_MODEL,
                max_tokens=CHAT_MAX_TOKENS,
                temperature=CHAT_TEMPERATURE,
                top_p=CHAT_TOP_P,
            )
        else:
            msg = f"Unsupported provider: {provider}"
            raise ValueError(msg)

    async def generate_response(
        self,
        system_prompt: str,
        messages: list[ChatMessage],
        provider: ProviderType | None = None,
    ) -> ResponseResult:
        """Generate a response using the specified or current provider.

        Parameters
        ----------
        system_prompt : str
            The system prompt to use.
        messages : list[ChatMessage]
            The conversation messages.
        provider : ProviderType | None
            Optional provider override. If None, uses current setting.

        Returns
        -------
        ResponseResult
            The response from the AI provider.

        Raises
        ------
        ValueError
            If the provider is unsupported or model is not configured.
        """
        if provider is None:
            provider = self._provider_manager.get_provider()

        if CHAT_MODEL is None:
            msg = "Chat model is not configured"
            raise ValueError(msg)

        model_params = self._create_model_params(provider)

        logger.info("Generating response using provider: %s", provider)

        if provider == "openai":
            return await generate_openai_response(
                system_prompt=system_prompt,
                prompt=messages,
                model_params=model_params,
            )
        elif provider == "anthropic":  # noqa: RET505
            return await generate_anthropic_response(
                prompt=messages,
                model_params=model_params,
                system_prompt=system_prompt,
            )
        elif provider == "google":
            return await generate_gemini_response(
                prompt=messages,
                model_params=model_params,
                system_prompt=system_prompt,
            )
        else:
            msg = f"Unsupported provider: {provider}"
            raise ValueError(msg)
