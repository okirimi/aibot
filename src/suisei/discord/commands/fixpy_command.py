from discord import (
    Interaction,
    TextStyle,
)
from discord.ui import Modal, TextInput

from src.suisei.adapters.chat import ChatMessage
from src.suisei.cli import logger
from src.suisei.discord.client import BotClient
from src.suisei.env import (
    FIXPY_MAX_TOKENS,
    FIXPY_MODEL,
    FIXPY_TEMPERATURE,
    FIXPY_TOP_P,
)
from src.suisei.infrastructure.api.anthropic_api import generate_anthropic_response
from src.suisei.types import ClaudeParams
from src.suisei.yml import FIXPY_SYSTEM

_client: BotClient = BotClient.get_instance()


class CodeModal(Modal):
    """Modal for entering Python code to fix."""

    code_input: TextInput

    def __init__(self) -> None:
        """Initialize the code modal with AI parameters."""
        super().__init__(title="Pythonバグバスター")

        self.code_input = TextInput(
            label="fixpy",
            style=TextStyle.long,
            placeholder="コードを入力してください",
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

            if FIXPY_MODEL is None:
                await interaction.followup.send(
                    "**ERROR** - 利用可能なモデルがありません",
                    ephemeral=True,
                )
                return

            params = ClaudeParams(
                model=FIXPY_MODEL,
                max_tokens=FIXPY_MAX_TOKENS,
                temperature=FIXPY_TEMPERATURE,
                top_p=FIXPY_TOP_P,
            )

            message = [ChatMessage(role="user", content=code)]

            response = await generate_anthropic_response(
                system_prompt=FIXPY_SYSTEM,
                prompt=message,
                model_params=params,
            )

            if response.result is not None:
                await interaction.followup.send(
                    f"{response.result}",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "**ERROR** - AIサービスからの応答の生成に失敗しました",
                    ephemeral=True,
                )
        except Exception as err:
            msg = f"Error processing fixpy command request: {err!s}"
            logger.exception(msg)
            await interaction.followup.send(
                "**ERROR** - fixpyコマンドの処理中にエラーが発生しました",
                ephemeral=True,
            )


@_client.tree.command(name="fixpy", description="Pythonコードのバグを特定し修正します")
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

        if FIXPY_MODEL is None:
            await interaction.response.send_message(
                "**ERROR** - 利用可能なモデルがありません",
                ephemeral=True,
            )
            return

        # Show the modal to input code
        modal = CodeModal()
        await interaction.response.send_modal(modal)

    except Exception as err:
        msg = f"Error showing fixpy modal: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**ERROR** - コマンドの実行中にエラーが発生しました",
            ephemeral=True,
        )
