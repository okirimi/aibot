import asyncio
import os
import signal
from collections.abc import Generator
from contextlib import contextmanager

from src.aibot.cli import logger
from src.aibot.discord.client import BotClient
from src.aibot.discord.commands import *
from src.aibot.infrastructure.db.dao.access_dao import AccessLevelDAO


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
    """Entry point for the 'SuiseiBot'."""
    # Initialize database tables
    await AccessLevelDAO().create_table()

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
