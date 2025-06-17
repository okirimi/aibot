from discord import Interaction, app_commands

from src.aibot.adapters.chat import ChatMessage
from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.env import (
    CHAT_MAX_TOKENS,
    CHAT_MODEL,
    CHAT_TEMPERATURE,
    CHAT_TOP_P,
)
from src.aibot.infrastructure.api.openai_api import generate_openai_response
from src.aibot.json import get_text
from src.aibot.types import GPTParams
from src.aibot.utils.decorators.access import is_not_blocked_user
from src.aibot.yml import CHAT_SYSTEM

_client = BotClient().get_instance()


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

        if CHAT_MODEL is None:
            await interaction.followup.send(
                get_text("errors.no_available_model"),
                ephemeral=True,
            )
            logger.error("Chat model is not set.")
            return

        model_params = GPTParams(
            model=CHAT_MODEL,
            max_tokens=CHAT_MAX_TOKENS,
            temperature=CHAT_TEMPERATURE,
            top_p=CHAT_TOP_P,
        )

        message = ChatMessage(role="user", content=user_msg)

        response = await generate_openai_response(
            system_prompt=CHAT_SYSTEM,
            prompt=[message],
            model_params=model_params,
        )

        await interaction.followup.send(f"{response.result}")
    except Exception as err:
        msg = f"Error in chat command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            get_text("errors.chat_command_processing_error"),
            ephemeral=True,
        )
