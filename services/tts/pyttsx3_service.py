"""pyttsx3 offline TTS fallback using Windows SAPI5.

pyttsx3 requires calling runAndWait() from the thread that created
the engine (COM STA restriction on Windows).  We solve this by running
the engine in its own dedicated daemon thread fed via a Queue.
"""

import queue
import threading
from typing import Coroutine

from loguru import logger

from services.tts.base import TTSBase

_STOP_SENTINEL = object()


class Pyttsx3Service(TTSBase):
    """Offline TTS using pyttsx3 (Windows SAPI5 voices).

    Safe for cross-thread use — internally marshals speak() calls
    through a Queue to the engine's dedicated thread.
    """

    def __init__(self, rate: int = 185):
        self._rate = rate
        self._queue: queue.Queue = queue.Queue()
        self._speaking = False
        self._thread = threading.Thread(target=self._engine_thread, daemon=True)
        self._thread.start()

    def _engine_thread(self) -> None:
        """Dedicated thread that owns the pyttsx3 engine."""
        try:
            import pyttsx3
        except ImportError:
            logger.error("pyttsx3 not installed. Run: pip install pyttsx3")
            return

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            logger.debug(f"pyttsx3 engine ready (rate={self._rate})")
        except Exception as exc:
            logger.error(f"pyttsx3 init failed: {exc}")
            return

        while True:
            item = self._queue.get()
            if item is _STOP_SENTINEL:
                break
            text = item
            try:
                self._speaking = True
                engine.say(text)
                engine.runAndWait()
                self._speaking = False
            except Exception as exc:
                self._speaking = False
                logger.exception(f"pyttsx3 speak failed: {exc}")

    async def speak(self, text: str) -> None:
        """Queue text for speech. Returns immediately (non-blocking)."""
        if text.strip():
            self._queue.put(text)

    def stop(self) -> None:
        """Stop current speech (best-effort; pyttsx3 stop is limited)."""
        # pyttsx3 doesn't support mid-sentence stop reliably.
        # Flush the queue to prevent queued sentences from playing.
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._speaking = False

    def is_speaking(self) -> bool:
        return self._speaking

    def shutdown(self) -> None:
        """Signal the engine thread to exit cleanly."""
        self._queue.put(_STOP_SENTINEL)
