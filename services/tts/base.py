"""Abstract base for text-to-speech services."""

from abc import ABC, abstractmethod


class TTSBase(ABC):
    """All TTS implementations must satisfy this interface."""

    @abstractmethod
    async def speak(self, text: str) -> None:
        """Convert text to speech and play audio.

        Args:
            text: The string to speak aloud.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """Immediately stop any ongoing speech playback."""
        ...

    @abstractmethod
    def is_speaking(self) -> bool:
        """Return True if audio is currently playing."""
        ...
