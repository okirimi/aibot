"""Translation JSON utility module for fetching localized strings."""

import json
from pathlib import Path
from typing import Any

from src.aibot.cli import logger
from src.aibot.env import LANGUAGE

# Base path to translation files
TRANSLATION_DIR = Path(__file__).parent.parent.parent / "i18n"


class TranslationManager:
    """Manager class for handling translation JSON files."""

    def __init__(self) -> None:
        """Initialize the TranslationManager."""
        self._translations: dict[str, dict[str, Any]] = {}
        self._bot_language: str = LANGUAGE  # Bot language setting from environment variable
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files from the i18n directory."""
        self._translations.clear()

        if not TRANSLATION_DIR.exists():
            logger.warning("Translation directory not found: %s", TRANSLATION_DIR)
            self._translations = {"en": {}, "ja": {}}
            return

        try:
            # Discover and load all translation-*.json files
            for translation_file in TRANSLATION_DIR.glob("translation-*.json"):
                # Extract language code from filename (e.g., "translation-en.json" -> "en")
                language_code = translation_file.stem.replace("translation-", "")

                try:
                    with translation_file.open("r", encoding="utf-8") as f:
                        self._translations[language_code] = json.load(f)
                    logger.info(
                        "Loaded %s translations from %s",
                        language_code,
                        translation_file.name,
                    )
                except json.JSONDecodeError as json_err:
                    logger.error("Invalid JSON in %s: %s", translation_file.name, json_err)
                except Exception as file_err:
                    logger.error("Failed to load %s: %s", translation_file.name, file_err)

            # Ensure we have at least English and Japanese entries
            if "en" not in self._translations:
                logger.warning("English translations not found, creating empty entry")
                self._translations["en"] = {}
            if "ja" not in self._translations:
                logger.warning("Japanese translations not found, creating empty entry")
                self._translations["ja"] = {}

        except Exception as err:
            logger.exception("Failed to load translation files: %s", err)
            self._translations = {"en": {}, "ja": {}}

    def get_text(self, key: str, language: str | None = None, **kwargs: str | int) -> str:
        """Get translated text by key path.

        Parameters
        ----------
        key : str
            Dot-separated key path (e.g., "commands.chat.description")
        language : str | None, optional
            Language code ("en" or "ja"), by default uses bot's language
        **kwargs : str | int
            Values for placeholder replacement (e.g., user_id=123, access_level="advanced")

        Returns
        -------
        str
            Translated text with placeholders replaced, or the key if not found

        Examples
        --------
        >>> manager = TranslationManager()
        >>> manager.get_text("commands.chat.description")
        'Perform a single-turn chat with AI'
        >>> manager.get_text(
        ...     "access_control.access_level_granted", user_id=123, access_level="advanced"
        ... )
        'Access level `advanced` has been granted to the user (ID: `123`)'
        """
        if language is None:
            language = self._bot_language

        if language not in self._translations:
            logger.warning("Language '%s' not available, falling back to 'en'", language)
            language = "en"

        translation_data = self._translations.get(language, {})

        # Navigate through nested keys
        current_data = translation_data
        keys = key.split(".")

        try:
            for k in keys:
                current_data = current_data[k]

            text = str(current_data)

            # Replace placeholders if kwargs provided
            if kwargs:
                text = text.format(**kwargs)
        except (KeyError, TypeError, ValueError) as err:
            logger.warning(
                "Translation key '%s' not found for language '%s': %s",
                key,
                language,
                err,
            )
            return key  # Return the key itself as fallback
        else:
            return text

    def get_bot_language(self) -> str:
        """Get the current bot language.

        Returns
        -------
        str
            Current bot language code
        """
        return self._bot_language


class TranslationManagerSingleton:
    """Singleton wrapper for TranslationManager to avoid global state issues."""

    _instance: TranslationManager | None = None

    @classmethod
    def get_instance(cls) -> TranslationManager:
        """Get the singleton TranslationManager instance.

        Returns
        -------
        TranslationManager
            Singleton TranslationManager instance
        """
        if cls._instance is None:
            cls._instance = TranslationManager()
        return cls._instance


def get_translation_manager() -> TranslationManager:
    """Get the global TranslationManager instance.

    Returns
    -------
    TranslationManager
        Global TranslationManager instance
    """
    return TranslationManagerSingleton.get_instance()


def get_bot_language() -> str:
    """Get the current global bot language.

    Returns
    -------
    str
        Current bot language code
    """
    manager = get_translation_manager()
    return manager.get_bot_language()


def get_text(key: str, language: str | None = None, **kwargs: str | int) -> str:
    """Get translated text by key path.

    Parameters
    ----------
    key : str
        Dot-separated key path (e.g., "commands.chat.description")
    language : str | None, optional
        Language code ("en" or "ja"), by default uses bot's language
    **kwargs : str | int
        Values for placeholder replacement

    Returns
    -------
    str
        Translated text with placeholders replaced
    """
    manager = get_translation_manager()
    return manager.get_text(key, language, **kwargs)
