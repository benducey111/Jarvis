"""Wake word detection stub.

This module provides the interface for always-on wake word detection.
A real implementation can be wired in using pvporcupine or openwakeword.

Usage (future):
    from core.wake_word import WakeWordDetector

    detector = WakeWordDetector(keyword="jarvis", on_detected=callback)
    detector.start()
"""

from abc import ABC, abstractmethod
from typing import Callable


class WakeWordDetectorBase(ABC):
    """Abstract base for wake word detection backends."""

    @abstractmethod
    def start(self) -> None:
        """Begin always-on listening for the wake word."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop listening."""
        ...

    @abstractmethod
    def is_running(self) -> bool:
        """Return True if detection is active."""
        ...


class StubWakeWordDetector(WakeWordDetectorBase):
    """Stub implementation — does nothing.

    Replace with a pvporcupine or openwakeword implementation in V2.

    Example pvporcupine integration:
        import pvporcupine
        handle = pvporcupine.create(keywords=["jarvis"])
        # audio loop: if handle.process(pcm_frame) >= 0: on_detected()
    """

    def __init__(self, keyword: str = "jarvis",
                 on_detected: Callable | None = None):
        self._keyword = keyword
        self._on_detected = on_detected
        self._running = False

    def start(self) -> None:
        self._running = True
        # TODO: integrate pvporcupine or openwakeword here

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running
