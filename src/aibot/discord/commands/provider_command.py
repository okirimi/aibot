from discord import Interaction, SelectOption
from discord.ui import Select, View

from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.json import get_text
from src.aibot.services.provider_manager import ProviderManager, ProviderType
from src.aibot.utils.decorators.access import is_not_blocked_user

_client = BotClient().get_instance()
_provider_manager = ProviderManager.get_instance()


class ProviderSelector(Select):
    """Discord UI selector for choosing AI providers.

    This class creates a dropdown menu that allows users to
    select between different AI providers (OpenAI, Anthropic, Google).
    """

    def __init__(self) -> None:
        """Initialize the provider selector with available options."""
        options = [
            SelectOption(
                label="OpenAI",
                value="openai",
                description="Use OpenAI API",
            ),
            SelectOption(
                label="Anthropic",
                value="anthropic",
                description="Use Anthropic API",
            ),
            SelectOption(
                label="Google",
                value="google",
                description="Use Google Gemini API",
            ),
        ]

        super().__init__(
            placeholder=get_text("provider.select_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Handle the user's selection of AI provider.

        Parameters
        ----------
        interaction : Interaction
            The Discord interaction context.
        """
        try:
            # Defer the response first
            await interaction.response.defer(ephemeral=True)

            chosen_provider: ProviderType = self.values[0]  # type: ignore[assignment]

            # Update the global provider setting
            _provider_manager.set_provider(chosen_provider)

            # Get display name for user feedback
            display_name = _provider_manager.get_provider_display_name()

            await interaction.followup.send(
                get_text("provider.provider_set", provider=display_name),
                ephemeral=True,
            )

            logger.info(
                "User (%s) changed AI provider to: %s",
                interaction.user,
                chosen_provider,
            )
        except Exception as e:
            logger.error("Failed to change provider: %s", e)
            await interaction.followup.send(
                get_text("errors.command_processing_error"),
                ephemeral=True,
            )


@_client.tree.command(name="provider", description=get_text("commands.provider.description"))
@is_not_blocked_user()
async def provider_command(interaction: Interaction) -> None:
    """Select the AI provider to use for chat commands.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("User (%s) is executing provider command", user)

        # Show current provider
        current_provider = _provider_manager.get_provider_display_name()
        current_provider_message = get_text(
            "provider.current_provider",
            provider=current_provider,
        )

        # Create the selector
        selector = ProviderSelector()
        view = View()
        view.add_item(selector)

        await interaction.response.send_message(
            f"{current_provider_message}\n\n{get_text('provider.selection_message')}",
            view=view,
            ephemeral=True,
        )

    except Exception as err:
        msg = f"Error in provider command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            get_text("errors.command_processing_error"),
            ephemeral=True,
        )
