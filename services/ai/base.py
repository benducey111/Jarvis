"""Abstract base for AI chat backends."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator


class AIBase(ABC):
    """All AI backends must satisfy this interface.

    The abstraction uses the standard OpenAI messages list format:
        [{"role": "system" | "user" | "assistant", "content": "..."}]
    """

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]]) -> str:
        """Send messages and return a complete response string.

        Args:
            messages: Conversation history in OpenAI format.

        Returns:
            Full assistant response as a single string.
        """
        ...

    @abstractmethod
    async def stream_chat(
        self, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Send messages and yield response tokens as they arrive.

        Args:
            messages: Conversation history in OpenAI format.

        Yields:
            Token strings (partial words or punctuation chunks).
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the backend is configured and reachable."""
        ...
