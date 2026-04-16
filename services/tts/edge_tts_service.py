"""edge-tts text-to-speech service.

Uses playsound for audio playback — pure Python, no compilation required,
works on Python 3.14 via Windows native MCI audio APIs.
"""

import asyncio
import io
import os
import tempfile
import threading

from loguru import logger

from services.tts.base import TTSBase


class EdgeTTSService(TTSBase):
    """Neural TTS using Microsoft Edge's speech synthesis (free, requires internet).

    Audio is collected into memory, written to a temporary MP3 file, played via
    playsound (Windows MCI), then the temp file is deleted.  This approach works
    on Python 3.14 without any compiled dependencies.
    """

    def __init__(self, voice: str = "en-US-GuyNeural", rate: str = "+0%",
                 volume: str = "+0%"):
        self._voice = voice
        self._rate = rate
        self._volume = volume
        self._speaking = False
        self._stop_event = threading.Event()

    async def speak(self, text: str) -> None:
        """Convert text to speech and play audio (blocking until done)."""
        if not text.strip():
            return

        try:
            import edge_tts
        except ImportError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
            return

        try:
            communicate = edge_tts.Communicate(
                text, voice=self._voice, rate=self._rate, volume=self._volume
            )
            audio_buffer = io.BytesIO()

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])

            audio_data = audio_buffer.getvalue()
            if not audio_data:
                logger.warning("edge-tts returned empty audio")
                return

            # Run blocking playback in executor so we don't block the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._play_audio, audio_data)

        except Exception as exc:
            logger.exception(f"edge-tts speak failed: {exc}")
        finally:
            self._speaking = False

    def _play_audio(self, audio_data: bytes) -> None:
        """Write MP3 bytes to a temp file and play via playsound (blocking)."""
        tmp_path = None
        try:
            # Write to a named temp file (playsound needs a file path)
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False, prefix="jarvis_tts_"
            ) as f:
                f.write(audio_data)
                tmp_path = f.name

            self._speaking = True
            self._stop_event.clear()

            try:
                from playsound import playsound
                playsound(tmp_path, block=True)
            except ImportError:
                # Fallback: use Windows built-in MCI via ctypes (no extra deps)
                self._play_via_winsound_fallback(tmp_path)

        except Exception as exc:
            logger.exception(f"Audio playback failed: {exc}")
        finally:
            self._speaking = False
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass  # File locked briefly after playback; will be cleaned up later

    def _play_via_winsound_fallback(self, mp3_path: str) -> None:
        """Last-resort playback using Windows MCI directly via ctypes."""
        import ctypes
        winmm = ctypes.windll.winmm

        alias = "jarvis_audio"
        open_cmd = f'open "{mp3_path}" type mpegvideo alias {alias}'
        play_cmd = f"play {alias} wait"
        close_cmd = f"close {alias}"

        winmm.mciSendStringW(open_cmd, None, 0, 0)
        winmm.mciSendStringW(play_cmd, None, 0, 0)
        winmm.mciSendStringW(close_cmd, None, 0, 0)

    def stop(self) -> None:
        """Request playback to stop (best-effort for playsound)."""
        self._stop_event.set()
        self._speaking = False
        # playsound block=True doesn't support mid-playback stop;
        # for real stop, the pyttsx3 fallback or OS-level process kill is needed.

    def is_speaking(self) -> bool:
        return self._speaking
