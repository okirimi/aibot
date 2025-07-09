import asyncio
import os
import signal
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv

from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.discord.commands import *
from src.aibot.infrastructure.db.dao.access_dao import AccessLevelDAO
from src.aibot.infrastructure.db.dao.prompt_dao import PromptDAO
from src.aibot.infrastructure.db.dao.system_config_dao import SystemConfigDAO


@contextmanager
def ignore_signals(signals: list[signal.Signals]) -> Generator[None, None, None]:
    """Temporarily ignore specified signals.

    Parameters
    ----------
    signals : list[signal.Signals]
        A list of signals to ignore.

    Examples
    --------
    >>> with ignore_signals([signal.SIGTERM, signal.SIGINT]):
    ...     # processes whose signals are ignored
    ...     pass
    """
    original_handlers = {sig: signal.getsignal(sig) for sig in signals}
    try:
        for sig in signals:
            signal.signal(sig, signal.SIG_IGN)
        yield
    finally:
        for sig, handler in original_handlers.items():
            signal.signal(sig, handler)


async def main() -> None:
    """Entry point for the 'AiBot'."""
    # Initialize database tables
    await AccessLevelDAO().create_table()
    await PromptDAO().create_table()
    await SystemConfigDAO().create_table()

    # Disable force system mode to allow user system prompt customization
    system_config_dao = SystemConfigDAO()
    await system_config_dao.disable_force_system()
    logger.info("Force system mode disabled - users can now customize system prompts")

    load_dotenv()
    # This system environment variable is specific to this function
    DISCORD_BOT_TOKEN: str = os.environ["DISCORD_BOT_TOKEN"]  # noqa: N806

    client = BotClient.get_instance()

    try:
        await client.start(DISCORD_BOT_TOKEN)
    except Exception:
        logger.exception("An unexpected error occurred")
    finally:
        with ignore_signals([signal.SIGTERM, signal.SIGINT]):
            await client.cleanup_hook()
            logger.info("Cleanup process finished")


if __name__ == "__main__":
    asyncio.run(main())
