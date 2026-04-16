"""edge-tts text-to-speech service with pygame audio playback."""

import asyncio
import io
import threading

from loguru import logger

from services.tts.base import TTSBase


class EdgeTTSService(TTSBase):
    """Neural TTS using Microsoft Edge's speech synthesis (free, requires internet).

    Produces high-quality neural voices. Falls back to pyttsx3 if unavailable.
    """

    def __init__(self, voice: str = "en-US-GuyNeural", rate: str = "+0%",
                 volume: str = "+0%"):
        self._voice = voice
        self._rate = rate
        self._volume = volume
        self._speaking = False
        self._mixer_ready = False
        self._init_mixer()

    def _init_mixer(self) -> None:
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=2048)
            self._mixer_ready = True
            logger.debug("pygame mixer initialised for edge-tts playback")
        except ImportError:
            logger.warning("pygame not installed. Run: pip install pygame")
        except Exception as exc:
            logger.warning(f"pygame mixer init failed: {exc}")

    async def speak(self, text: str) -> None:
        """Convert text to speech using edge-tts and play via pygame."""
        if not text.strip():
            return

        try:
            import edge_tts
        except ImportError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
            return

        try:
            communicate = edge_tts.Communicate(text, voice=self._voice,
                                               rate=self._rate, volume=self._volume)
            audio_buffer = io.BytesIO()

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])

            audio_buffer.seek(0)
            audio_data = audio_buffer.read()

            if not audio_data:
                logger.warning("edge-tts returned empty audio")
                return

            self._play_audio(audio_data)

        except Exception as exc:
            logger.exception(f"edge-tts speak failed: {exc}")

    def _play_audio(self, audio_data: bytes) -> None:
        """Play MP3 audio bytes via pygame.mixer (blocking until done)."""
        if not self._mixer_ready:
            logger.warning("Mixer not ready — cannot play audio")
            return

        try:
            import pygame

            self._speaking = True
            sound = pygame.mixer.Sound(io.BytesIO(audio_data))
            channel = sound.play()
            if channel:
                while channel.get_busy():
                    pygame.time.wait(50)
            self._speaking = False
        except Exception as exc:
            self._speaking = False
            logger.exception(f"Audio playback failed: {exc}")

    def stop(self) -> None:
        """Immediately stop audio playback."""
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.stop()
        except Exception:
            pass
        self._speaking = False

    def is_speaking(self) -> bool:
        try:
            import pygame
            if pygame.mixer.get_init():
                return pygame.mixer.get_busy()
        except Exception:
            pass
        return self._speaking
