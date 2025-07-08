from discord import Interaction, app_commands

from src.aibot.adapters.chat import ChatMessage
from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.infrastructure.api.factory import ApiFactory
from src.aibot.json import get_text
from src.aibot.services.provider_manager import ProviderManager
from src.aibot.services.prompt_manager import get_prompt_manager
from src.aibot.utils.decorators.access import is_not_blocked_user
from src.aibot.yml import CHAT_SYSTEM_DEFAULT

_api_factory = ApiFactory()
_client = BotClient().get_instance()
_prompt_manager = get_prompt_manager()
_provider_manager = ProviderManager.get_instance()


@_client.tree.command(name="chat", description=get_text("commands.chat.description"))
@is_not_blocked_user()
@app_commands.rename(user_msg=get_text("commands.chat.parameter_names.message"))
async def chat_command(interaction: Interaction, user_msg: str) -> None:
    """Single-turn chat with the bot.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.

    user_msg : str
        The message to send to the bot.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) is executing chat command", user)

        await interaction.response.defer()

        message = ChatMessage(role="user", content=user_msg)

        # Get dynamic system prompt or fallback to static
        try:
            system_prompt = await _prompt_manager.get_chat_system_prompt()
        except Exception as e:
            logger.warning("Failed to get dynamic system prompt, using static: %s", e)
            system_prompt = CHAT_SYSTEM_DEFAULT

        # Get current provider and generate response
        current_provider = _provider_manager.get_provider()
        logger.debug("Using AI provider: %s for chat", current_provider)

        response = await _api_factory.generate_response(
            system_prompt=system_prompt,
            messages=[message],
        )

        await interaction.followup.send(f"{response.result}")
    except Exception as err:
        msg = f"Error in chat command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            get_text("errors.chat_command_processing_error"),
            ephemeral=True,
        )
