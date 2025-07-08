from discord import Interaction, TextStyle, app_commands, ui

from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.json import get_text
from src.aibot.services.prompt_manager import get_prompt_manager
from src.aibot.utils.decorators.access import is_not_blocked_user

_client = BotClient().get_instance()
_prompt_manager = get_prompt_manager()


class SystemPromptModal(ui.Modal, title=get_text("system.modal_title")):
    """Modal for setting system prompts."""

    def __init__(self) -> None:
        """Initialize the modal."""
        super().__init__()

    prompt_input: ui.TextInput = ui.TextInput(
        label=get_text("system.prompt_input_label"),
        placeholder=get_text("system.prompt_input_placeholder"),
        style=TextStyle.paragraph,
        required=True,
        max_length=4000,
    )

    async def on_submit(self, interaction: Interaction) -> None:
        """Handle modal submission.

        Parameters
        ----------
        interaction : Interaction
            The interaction instance.
        """
        try:
            user = interaction.user
            logger.info("User ( %s ) is setting system prompt", user)

            await interaction.response.defer(ephemeral=True)

            # Create and activate the new system prompt
            result = await _prompt_manager.service.create_prompt_from_modal(
                prompt_content=self.prompt_input.value,
                created_by=user.id,
                auto_activate=True,
            )

            if result and result.get("success"):
                logger.info(
                    "System prompt created and activated (ID: %d) for user %s",
                    result["prompt_id"],
                    user,
                )
                await interaction.followup.send(
                    get_text("system.prompt_set"),
                    ephemeral=True,
                )
            else:
                logger.error("Failed to create system prompt for user %s", user)
                await interaction.followup.send(
                    get_text("system.prompt_creation_failed"),
                    ephemeral=True,
                )

        except Exception as err:
            msg = f"Error in system command modal: {err!s}"
            logger.exception(msg)
            await interaction.followup.send(
                get_text("errors.system_command_processing_error"),
                ephemeral=True,
            )


@_client.tree.command(name="system", description=get_text("commands.system.description"))
@is_not_blocked_user()
async def system_command(interaction: Interaction) -> None:
    """Set system prompt for chat commands.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) is opening system prompt modal", user)

        modal = SystemPromptModal()
        await interaction.response.send_modal(modal)

    except Exception as err:
        msg = f"Error in system command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            get_text("errors.system_command_processing_error"),
            ephemeral=True,
        )
