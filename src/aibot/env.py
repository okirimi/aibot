from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytz
from dotenv import load_dotenv

from src.aibot.cli import logger

if TYPE_CHECKING:
    from pytz import _UTCclass
    from pytz.tzinfo import DstTzInfo, StaticTzInfo

load_dotenv()

# ========== These variables are system environment variables ==========

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    logger.warning("Anthropic API key is not set. Using empty string.")

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logger.warning("OpenAI API key is not set. Using empty string.")

DISCORD_BOT_TOKEN: str = os.environ["DISCORD_BOT_TOKEN"]

# ========== Environment variables that defined in .env file ==========

ADMIN_USER_IDS: list[int] = [
    int(id_str) for id_str in os.environ["ADMIN_USER_IDS"].split(",") if id_str.strip()
]

AUTHORIZED_SERVER_IDS: list[int] = [
    int(id_str) for id_str in os.environ["AUTHORIZED_SERVER_IDS"].split(",") if id_str.strip()
]

BOT_NAME: str = os.environ["BOT_NAME"]

DB_NAME: str = os.environ["DB_NAME"]

CHAT_MAX_TOKENS: int = int(os.environ["CHAT_MAX_TOKENS"])
CHAT_MODEL: str = os.environ["CHAT_MODEL"]
CHAT_TEMPERATURE: float = float(os.environ["CHAT_TEMPERATURE"])
CHAT_TOP_P: float = float(os.environ["CHAT_TOP_P"])

FIXPY_MAX_TOKENS: int = int(os.environ["FIXPY_MAX_TOKENS"])
FIXPY_MODEL: str = os.environ["FIXPY_MODEL"]
FIXPY_TEMPERATURE: float = float(os.environ["FIXPY_TEMPERATURE"])
FIXPY_TOP_P: float = float(os.environ["FIXPY_TOP_P"])

MAX_CHARS_PER_MESSAGE: int = int(os.environ["MAX_CHARS_PER_MESSAGE"])

LANGUAGE: str = os.environ["LANGUAGE"]

_tz: str = os.environ["TIMEZONE"]
TIMEZONE: _UTCclass | DstTzInfo | StaticTzInfo = pytz.timezone(_tz)
