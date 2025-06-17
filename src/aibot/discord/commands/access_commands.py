from discord import Interaction, SelectOption, User
from discord.ui import Select, View

from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.infrastructure.db.dao.access_dao import AccessLevelDAO
from src.aibot.utils.decorators.access import is_admin_user, is_not_blocked_user

_client: BotClient = BotClient.get_instance()
access_dao = AccessLevelDAO()


async def _validate_guild_and_user(interaction: Interaction, user: User) -> tuple[bool, int]:
    """Validate that the command is run in a guild and the user exists in the guild.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to validate.

    Returns
    -------
    tuple[bool, int]
        A tuple containing:
        - bool: True if validation passed, False if failed
        - int: The user ID if validation passed, 0 if failed
    """
    target_user_id: int = user.id

    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a guild",
            ephemeral=True,
        )
        return False, 0

    target_user = interaction.guild.get_member(target_user_id)
    if target_user is None:
        await interaction.response.send_message(
            "The user does not exist in the guild",
            ephemeral=True,
        )
        return False, 0

    return True, target_user_id


class AccessLevelGrantSelector(Select):
    """Discord UI selector for granting access levels to users.

    This class creates a dropdown menu that allows administrators to
    select access levels ('advanced' or 'blocked') to grant to a user.

    Parameters
    ----------
    user_id : int
        The Discord user ID to grant access level to.
    options : list[SelectOption]
        List of SelectOption objects representing available access levels.
    """

    def __init__(self, user_id: int, options: list[SelectOption]) -> None:
        self.user_id = user_id
        super().__init__(
            placeholder="Select an access level...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Handle the user's selection of access level to grant.

        Parameters
        ----------
        interaction : Interaction
            The Discord interaction context.

        Notes
        -----
        This callback inserts the selected access level for the user into the database
        and sends a confirmation message.
        """
        chosen = self.values[0]  # "advanced" or "blocked"
        if chosen == "advanced":
            await access_dao.grant(user_id=self.user_id, access_level="advanced")
        elif chosen == "blocked":
            await access_dao.grant(user_id=self.user_id, access_level="blocked")

        await interaction.response.send_message(
            f"Access level `{chosen}` has been granted to the user (ID: `{self.user_id}`)",
            ephemeral=True,
        )
        logger.info(
            "Access level <%s> has been granted to the user (ID: %s)",
            chosen,
            self.user_id,
        )


class AccessLevelRevokeSelector(Select):
    """Discord UI selector for revoking access levels for users.

    This class creates a dropdown menu that allows administrators to
    select access levels ('advanced' or 'blocked') to revoke for a user.

    Parameters
    ----------
    user_id : int
        The Discord user ID to revoke access level for.
    options : list[SelectOption]
        List of SelectOption objects representing available access levels.
    """

    def __init__(self, user_id: int, options: list[SelectOption]) -> None:
        self.user_id = user_id
        super().__init__(
            placeholder="Select an access level...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Handle the user's selection of access level to revoke.

        Parameters
        ----------
        interaction : Interaction
            The Discord interaction context.

        Notes
        -----
        This callback revokes the selected access level for the user in the database
        and sends a confirmation message.
        """
        chosen = self.values[0]  # "advanced" or "blocked"
        if chosen == "advanced":
            await access_dao.revoke(user_id=self.user_id, access_level="advanced")
        elif chosen == "blocked":
            await access_dao.revoke(user_id=self.user_id, access_level="blocked")

        await interaction.response.send_message(
            f"Access level `{chosen}` has been revoked from the user (ID: `{self.user_id}`)",
            ephemeral=True,
        )
        logger.info(
            "Access level <%s> has been revoked from the user (ID: %s)",
            chosen,
            self.user_id,
        )


@_client.tree.command(name="grant", description="Grant an access level to the user")
@is_admin_user()
@is_not_blocked_user()
async def grant_command(interaction: Interaction, user: User) -> None:
    """Grant access level to a Discord user.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to grant access level to.

    Notes
    -----
    This function grants 'advanced' or 'blocked' access level to the specified user.
    """
    is_valid, target_user_id = await _validate_guild_and_user(interaction, user)
    if not is_valid:
        return

    options = [
        SelectOption(label="advanced", value="advanced"),
        SelectOption(label="blocked", value="blocked"),
    ]

    select = AccessLevelGrantSelector(user_id=target_user_id, options=options)
    view = View()
    view.add_item(select)

    await interaction.response.send_message(
        "Select an access level to grant to the user",
        view=view,
        ephemeral=True,
    )


@_client.tree.command(name="check", description="Check the access level of the user")
@is_admin_user()
@is_not_blocked_user()
async def check_access_command(interaction: Interaction, user: User) -> None:
    """Check the access level of a Discord user.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to check access level for.

    Notes
    -----
    This function displays whether the user has 'advanced' or 'blocked' access level.
    """
    is_valid, target_user_id = await _validate_guild_and_user(interaction, user)
    if not is_valid:
        return

    advanced_user_ids = await access_dao.fetch_user_ids_by_access_level("advanced")
    blocked_user_ids = await access_dao.fetch_user_ids_by_access_level("blocked")

    if target_user_id in advanced_user_ids and target_user_id in blocked_user_ids:
        await interaction.response.send_message(
            f"The user (ID: `{target_user_id}`) has the access level `advanced` and `blocked`",
            ephemeral=True,
        )
        return
    if target_user_id in advanced_user_ids:
        await interaction.response.send_message(
            f"The user (ID: `{target_user_id}`) has the access level `advanced`",
            ephemeral=True,
        )
        return
    if target_user_id in blocked_user_ids:
        await interaction.response.send_message(
            f"The user (ID: `{target_user_id}`) has the access level `blocked`",
            ephemeral=True,
        )
        return
    await interaction.response.send_message(
        f"The user (ID: `{target_user_id}`) does not have any access level",
        ephemeral=True,
    )


@_client.tree.command(name="revoke", description="Revoke an access level for the user")
@is_admin_user()
@is_not_blocked_user()
async def revoke_command(interaction: Interaction, user: User) -> None:
    """Revoke access level for a Discord user.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to revoke access level for.

    Notes
    -----
    This function revokes 'advanced' or 'blocked' access level for the specified user.
    """
    is_valid, target_user_id = await _validate_guild_and_user(interaction, user)
    if not is_valid:
        return

    options = [
        SelectOption(label="advanced", value="advanced"),
        SelectOption(label="blocked", value="blocked"),
    ]

    select = AccessLevelRevokeSelector(user_id=target_user_id, options=options)
    view = View()
    view.add_item(select)

    await interaction.response.send_message(
        "Select an access level to revoke for the user",
        view=view,
        ephemeral=True,
    )
