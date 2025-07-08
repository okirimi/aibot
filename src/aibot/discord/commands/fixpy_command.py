from discord import (
    Interaction,
    TextStyle,
)
from discord.ui import Modal, TextInput

from src.aibot.adapters.chat import ChatMessage
from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.infrastructure.api.factory import ApiFactory
from src.aibot.json import get_text
from src.aibot.services.provider_manager import ProviderManager
from src.aibot.services.prompt_manager import get_prompt_manager
from src.aibot.yml import FIXPY_SYSTEM


_api_factory = ApiFactory()
_client: BotClient = BotClient.get_instance()
_prompt_manager = get_prompt_manager()
_provider_manager = ProviderManager.get_instance()



class CodeModal(Modal):
    """Modal for entering Python code to fix."""

    code_input: TextInput

    def __init__(self) -> None:
        """Initialize the code modal with AI parameters."""
        super().__init__(title=get_text("fixpy.modal_title"))

        self.code_input = TextInput(
            label=get_text("fixpy.code_input_label"),
            style=TextStyle.long,
            placeholder=get_text("fixpy.code_input_placeholder"),
            required=True,
        )
        self.add_item(self.code_input)

    async def on_submit(self, interaction: Interaction) -> None:
        """Handle the submission of the modal.

        Parameters
        ----------
        interaction : Interaction
            The interaction object from Discord.
        """
        await interaction.response.defer(thinking=True)

        try:
            code = self.code_input.value

            system_prompt = FIXPY_SYSTEM

            current_provider = _provider_manager.get_provider()
            logger.debug("Using AI provider: %s for fixpy", current_provider)

            message = [ChatMessage(role="user", content=code)]

            response = await _api_factory.generate_response(
                system_prompt=system_prompt,
                messages=message,
            )

            if response.result is not None:
                await interaction.followup.send(
                    f"{response.result}",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    get_text("errors.ai_response_generation_failed"),
                    ephemeral=True,
                )
        except Exception as err:
            msg = f"Error processing fixpy command request: {err!s}"
            logger.exception(msg)
            await interaction.followup.send(
                get_text("errors.fixpy_command_processing_error"),
                ephemeral=True,
            )


@_client.tree.command(name="fixpy", description=get_text("commands.fixpy.description"))
async def fixpy_command(
    interaction: Interaction,
) -> None:
    """Detect and fix bugs in Python code.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) executed 'fixpy' command", user)

        # Show the modal to input code
        modal = CodeModal()
        await interaction.response.send_modal(modal)

    except Exception as err:
        msg = f"Error showing fixpy modal: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            get_text("errors.fixpy_modal_execution_error"),
            ephemeral=True,
        )
