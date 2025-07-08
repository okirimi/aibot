from discord import Interaction, SelectOption, TextStyle, ui

from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.env import MAX_CHARS_PER_MESSAGE
from src.aibot.json import get_text
from src.aibot.services.prompt_manager import get_prompt_manager
from src.aibot.utils.decorators.access import (
    check_force_system_mode,
    is_admin_user,
    is_not_blocked_user,
)

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


class SystemPromptSelect(ui.Select):
    """Select menu for choosing system prompts."""

    def __init__(self, files_info: list[dict], action: str) -> None:
        """Initialize the select menu.

        Parameters
        ----------
        files_info : list[dict]
            List of file information dictionaries.
        action : str
            Action type: "view" or "reactivate".
        """
        self.files_info = files_info
        self.action = action

        options = [
            SelectOption(
                label=f"#{file_info['number']:02d}: {file_info['preview']}",
                description=f"ファイル: {file_info['filename']}",
                value=str(file_info["number"]),
            )
            for file_info in files_info[:25]  # Discord limit: 25 options
        ]

        if not options:
            options.append(
                SelectOption(
                    label="利用可能なプロンプトファイルがありません",
                    description="プロンプトファイルが見つかりませんでした",
                    value="none",
                ),
            )

        super().__init__(
            placeholder="システムプロンプトを選択してください...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Handle select menu callback."""
        try:
            if self.values[0] == "none":
                await interaction.response.send_message(
                    "利用可能なプロンプトファイルがありません。",
                    ephemeral=True,
                )
                return

            number = int(self.values[0])
            file_info = next((f for f in self.files_info if f["number"] == number), None)

            if not file_info:
                await interaction.response.send_message(
                    "選択されたファイルが見つかりません。",
                    ephemeral=True,
                )
                return

            if self.action == "view":
                # Display the full content
                content = file_info["full_content"]
                if len(content) > MAX_CHARS_PER_MESSAGE:
                    content = (
                        content[:MAX_CHARS_PER_MESSAGE] + "\n... (内容が長いため省略されました)"
                    )

                await interaction.response.send_message(
                    f"**{file_info['filename']}** の内容:\n```\n{content}\n```",
                    ephemeral=True,
                )

            elif self.action == "reactivate":
                await interaction.response.defer(ephemeral=True)

                # Reactivate the prompt
                result = await _prompt_manager.service.reactivate_prompt_by_number(
                    number=number,
                    created_by=interaction.user.id,
                )

                if result and result.get("success"):
                    message = (
                        f"プロンプト #{number:02d} を再設定しました。"
                        f"新しいプロンプトID: {result['new_prompt_id']}"
                    )
                    await interaction.followup.send(
                        message,
                        ephemeral=True,
                    )
                    logger.info(
                        "User %s reactivated prompt from file #%02d (new ID: %d)",
                        interaction.user,
                        number,
                        result["new_prompt_id"],
                    )
                else:
                    await interaction.followup.send(
                        f"プロンプト #{number:02d} の再設定に失敗しました。",
                        ephemeral=True,
                    )

        except Exception as e:
            logger.exception("Error in system prompt select callback: %s", e)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "エラーが発生しました。",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "エラーが発生しました。",
                    ephemeral=True,
                )


class SystemPromptView(ui.View):
    """View for system prompt selection."""

    def __init__(self, files_info: list[dict], action: str) -> None:
        """Initialize the view.

        Parameters
        ----------
        files_info : list[dict]
            List of file information dictionaries.
        action : str
            Action type: "view" or "reactivate".
        """
        super().__init__(timeout=300)
        self.add_item(SystemPromptSelect(files_info, action))


@_client.tree.command(name="system", description=get_text("commands.system.description"))
@is_not_blocked_user()
@check_force_system_mode()
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


@_client.tree.command(
    name="systemlist",
    description="利用可能なシステムプロンプトを一覧表示します",
)
@is_not_blocked_user()
async def system_list_command(interaction: Interaction) -> None:
    """List available system prompts.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) is viewing system prompt list", user)

        # Get available prompt files
        files_info = _prompt_manager.service.get_available_prompt_files()

        if not files_info:
            await interaction.response.send_message(
                "利用可能なシステムプロンプトファイルがありません。",
                ephemeral=True,
            )
            return

        # Create view with select menu
        view = SystemPromptView(files_info, "view")
        await interaction.response.send_message(
            f"**利用可能なシステムプロンプト一覧** ({len(files_info)}件)\n"
            "下のメニューからプロンプトを選択して内容を表示できます。",
            view=view,
            ephemeral=True,
        )

    except Exception as err:
        msg = f"Error in system-list command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "エラーが発生しました。システム管理者にお問い合わせください。",
            ephemeral=True,
        )


@_client.tree.command(name="reuse", description="過去のシステムプロンプトを再設定します")
@is_not_blocked_user()
@check_force_system_mode()
async def reuse_command(interaction: Interaction) -> None:
    """Reactivate a previous system prompt.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) is reactivating system prompt", user)

        # Get available prompt files
        files_info = _prompt_manager.service.get_available_prompt_files()

        if not files_info:
            await interaction.response.send_message(
                "再設定可能なシステムプロンプトファイルがありません。",
                ephemeral=True,
            )
            return

        # Create view with select menu for reactivation
        view = SystemPromptView(files_info, "reactivate")
        await interaction.response.send_message(
            f"**システムプロンプトの再設定** ({len(files_info)}件)\n"
            "下のメニューからプロンプトを選択して再設定できます。",
            view=view,
            ephemeral=True,
        )

    except Exception as err:
        msg = f"Error in resystem command: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "エラーが発生しました。システム管理者にお問い合わせください。",
            ephemeral=True,
        )


@_client.tree.command(
    name="forcesystem",
    description="デフォルトシステム指示を強制し、ユーザーのカスタム設定を無効化します",
)
@is_admin_user()
async def force_system_command(interaction: Interaction) -> None:
    """Force default system instructions and disable user customization.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("Admin ( %s ) is enabling force system mode", user)

        await interaction.response.defer(ephemeral=True)

        result = await _prompt_manager.service.enable_force_system_mode(user.id)

        if result.get("success"):
            await interaction.followup.send(
                f"{result['message']}",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"{result['message']}",
                ephemeral=True,
            )

    except Exception as err:
        msg = f"Error in forcesystem command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "強制システムモードの有効化中にエラーが発生しました。",
            ephemeral=True,
        )


@_client.tree.command(
    name="unlocksystem",
    description="強制システムモードを解除し、ユーザーのカスタム設定を再有効化します",
)
@is_admin_user()
async def unlock_system_command(interaction: Interaction) -> None:
    """Unlock system commands and re-enable user customization.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("Admin ( %s ) is disabling force system mode", user)

        await interaction.response.defer(ephemeral=True)

        result = await _prompt_manager.service.disable_force_system_mode(user.id)

        if result.get("success"):
            await interaction.followup.send(
                f"{result['message']}",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"{result['message']}",
                ephemeral=True,
            )

    except Exception as err:
        msg = f"Error in unlocksystem command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "強制システムモードの無効化中にエラーが発生しました。",
            ephemeral=True,
        )


@_client.tree.command(name="resetsystem", description="システム指示をデフォルトにリセットします")
@is_not_blocked_user()
@check_force_system_mode()
async def reset_system_command(interaction: Interaction) -> None:
    """Reset system prompt to default instructions.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) is resetting system prompt to default", user)

        await interaction.response.defer(ephemeral=True)

        result = await _prompt_manager.service.reset_to_default_system(user.id)

        if result.get("success"):
            await interaction.followup.send(
                f"{result['message']}",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"{result['message']}",
                ephemeral=True,
            )

    except Exception as err:
        msg = f"Error in resetsystem command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "システム指示のリセット中にエラーが発生しました。",
            ephemeral=True,
        )
