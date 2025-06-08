from collections.abc import Callable
from typing import TypeVar

from discord import Interaction, app_commands

from src.suisei.env import ADMIN_USER_IDS, AUTHORIZED_SERVER_IDS
from src.suisei.infrastructure.db.dao.access_dao import AccessLevelDAO

_T = TypeVar("_T")
access_dao: AccessLevelDAO = AccessLevelDAO()


def is_authorized_server() -> Callable[[_T], _T]:
    """Check if the server has been authorized by bot owner.

    Returns
    -------
    Callable[[_T], _T]
        A decorator checks whether the server is listed in the
        environment variable `AUTHORIZED_SERVER_IDS`.
    """

    def predicate(interaction: Interaction) -> bool:
        return interaction.guild_id in AUTHORIZED_SERVER_IDS

    return app_commands.check(predicate)


def is_admin_user() -> Callable[[_T], _T]:
    """Check if the user has administrative access level.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user executing command is
        listed in the environment variable `ADMIN_USER_IDS`.
    """

    def predicate(interaction: Interaction) -> bool:
        return interaction.user.id in ADMIN_USER_IDS

    return app_commands.check(predicate)


def is_advanced_user() -> Callable[[_T], _T]:
    """Check if the user has advanced access level.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user executing command is listed
        in the table `access_level` with `advanced` access level.
    """

    async def predicate(interaction: Interaction) -> bool:
        advanced_user_ids = await access_dao.fetch_user_ids_by_access_level(
            access_level="advanced",
        )
        return interaction.user.id in advanced_user_ids

    return app_commands.check(predicate)


def is_not_blocked_user() -> Callable[[_T], _T]:
    """Check if the user had not been blocked.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user executing command is not listed
        in the table `blocked_user` with `blocked` access level.
    """

    async def predicate(interaction: Interaction) -> bool:
        blocked_user_ids = await access_dao.fetch_user_ids_by_access_level(
            access_level="blocked",
        )
        return interaction.user.id not in blocked_user_ids

    return app_commands.check(predicate)
