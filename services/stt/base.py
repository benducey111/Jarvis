"""Abstract base for speech-to-text services."""

from abc import ABC, abstractmethod


class STTBase(ABC):
    """All STT implementations must satisfy this interface."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes to text.

        Args:
            audio_bytes: Raw 16kHz mono PCM16LE audio data.

        Returns:
            Transcribed text string (empty string on failure/silence).
        """
        ...

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if the model/service is loaded and ready."""
        ...
