from __future__ import annotations

from typing import Literal, cast

from discord import Message as DiscordMessage
from discord import MessageType

ChatRole = Literal["assistant", "developer", "user"]
BOT_NAME = "suisei"  # Internal bot name used in the codebase


class ChatMessage:
    """Represents a single chat message with a role and content.

    Attributes
    ----------
    role : ChatRole
        The role of the message sender, e.g., 'developer', 'assistant', or 'user'.
    content : str | None
        The content of the message. Defaults to None.
    """

    def __init__(self, role: str, content: str | None = None) -> None:
        if role == BOT_NAME:
            self.role: ChatRole = "assistant"
        # cast前にroleがdeveloperまたはassistantであることを確認
        elif role in ("developer", "assistant"):
            self.role = cast("ChatRole", role)
        else:
            self.role = "user"
        self.content = content

    def format_message(self) -> dict[str, str]:
        """Represent a single chat message with a role and content.

        Returns
        -------
        dict
            A dictionary with 'role' and 'content' keys.
        """
        return {
            "role": self.role,
            "content": self.content or "",
        }

    @classmethod
    async def from_discord_message(cls, message: DiscordMessage) -> ChatMessage | None:
        """Convert a DiscordMessage instance to a ChatMessage instance.

        Parameters
        ----------
        message : DiscordMessage
            A message from Discord, which may be a thread starter or a
            regular message.

        Returns
        -------
        ChatMessage | None
            A ChatMessage instance if the conversion is successful,
            otherwise None.

        Examples
        --------
        >>> discord_msg = ...  # Discord message object
        >>> chat_msg = await ChatMessage.from_discord_message(discord_msg)
        >>> if chat_msg:
        ...     print(chat_msg.format_message())
        """
        # Process thread starter message
        if (
            message.type == MessageType.thread_starter_message
            and message.reference is not None
            and message.reference.cached_message
            and message.reference.cached_message.embeds
            and message.reference.cached_message.embeds[0].fields
        ):
            field = message.reference.cached_message.embeds[0].fields[0]
            return cls(role=message.author.name, content=field.value)
        # Process regular message
        if message.content is not None:
            return cls(role=message.author.name, content=message.content)
        return None


class ChatHistory:
    """Manage a collection of chat messages.

    Attributes
    ----------
    messages : list[ChatMessage]
        A list of ChatMessage objects representing the chat history.
    """

    def __init__(self, messages: list[ChatMessage]) -> None:
        """Initialize ChatHistory with a list of ChatMessage objects.

        Parameters
        ----------
        messages : list[ChatMessage]
            A list of ChatMessage objects representing the chat history.
        """
        self.messages = messages

    def render_message(self) -> list[dict[str, str]]:
        """Render the chat messages into a list of dictionaries.

        Returns
        -------
        list[dict[str, str]]
            A list where each dictionary represents a chat message with
            'role' and 'content' keys.
        """
        return [message.format_message() for message in self.messages]
