"""Microphone capture with voice-activity detection.

Uses sounddevice for cross-platform audio capture and webrtcvad for
energy-based voice activity detection (VAD).  The capture loop runs
entirely in a background thread and emits audio chunks via a callback.
"""

import threading
from collections import deque
from typing import Callable

import numpy as np
from loguru import logger


class MicrophoneCapture:
    """Continuously listens to the microphone and emits audio chunks when
    speech is detected.

    Usage:
        def on_audio(audio_bytes: bytes):
            transcript = stt.transcribe(audio_bytes)

        mic = MicrophoneCapture(on_audio_callback=on_audio)
        mic.start_listening()  # non-blocking, runs in a thread
        ...
        mic.stop_listening()
    """

    def __init__(
        self,
        on_audio_callback: Callable[[bytes], None],
        sample_rate: int = 16000,
        channels: int = 1,
        vad_aggressiveness: int = 2,
        silence_threshold_ms: int = 800,
    ):
        self._callback = on_audio_callback
        self._sample_rate = sample_rate
        self._channels = channels
        self._vad_aggressiveness = vad_aggressiveness
        self._silence_frames = int(silence_threshold_ms / 30)  # 30ms frames

        self._recording = threading.Event()
        self._stop_flag = threading.Event()
        self._thread: threading.Thread | None = None

        # VAD operates on 10ms, 20ms, or 30ms frames at 16kHz
        self._frame_duration_ms = 30
        self._frame_size = int(sample_rate * self._frame_duration_ms / 1000)  # samples

        self._vad = None  # lazily initialised

    def start_listening(self) -> None:
        """Begin microphone capture in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.debug("MicrophoneCapture: started")

    def stop_listening(self) -> None:
        """Stop the capture thread."""
        self._stop_flag.set()
        if self._thread:
            self._thread.join(timeout=3)
        logger.debug("MicrophoneCapture: stopped")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _get_vad(self):
        """Lazily initialise webrtcvad.Vad."""
        if self._vad is None:
            try:
                import webrtcvad
                self._vad = webrtcvad.Vad(self._vad_aggressiveness)
            except ImportError:
                logger.warning(
                    "webrtcvad not installed — VAD disabled, all audio will be captured. "
                    "Install: pip install webrtcvad-wheels"
                )
                self._vad = False  # disabled sentinel
        return self._vad

    def _capture_loop(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            logger.error(
                "sounddevice not installed. Run: pip install sounddevice"
            )
            return

        vad = self._get_vad()
        ring_buffer: deque = deque(maxlen=self._silence_frames)
        voiced_frames: list[bytes] = []
        triggered = False

        logger.info(f"MicrophoneCapture: listening at {self._sample_rate}Hz")

        with sd.RawInputStream(
            samplerate=self._sample_rate,
            blocksize=self._frame_size,
            channels=self._channels,
            dtype="int16",
        ) as stream:
            while not self._stop_flag.is_set():
                raw_bytes, _ = stream.read(self._frame_size)
                frame = bytes(raw_bytes)

                if vad and isinstance(vad, object) and vad is not False:
                    try:
                        is_speech = vad.is_speech(frame, self._sample_rate)
                    except Exception:
                        is_speech = True  # fail open
                else:
                    # VAD unavailable — treat everything as speech
                    is_speech = True

                if not triggered:
                    ring_buffer.append((frame, is_speech))
                    num_voiced = sum(1 for _, s in ring_buffer if s)
                    # Start recording when >60% of ring buffer is voiced
                    if num_voiced > 0.6 * ring_buffer.maxlen:
                        triggered = True
                        voiced_frames.extend(f for f, _ in ring_buffer)
                        ring_buffer.clear()
                        logger.debug("MicrophoneCapture: speech detected, recording…")
                else:
                    voiced_frames.append(frame)
                    ring_buffer.append((frame, is_speech))
                    num_unvoiced = sum(1 for _, s in ring_buffer if not s)
                    # Stop recording when silence fills the ring buffer
                    if num_unvoiced > 0.9 * ring_buffer.maxlen:
                        logger.debug(
                            f"MicrophoneCapture: silence detected, "
                            f"emitting {len(voiced_frames)} frames"
                        )
                        audio_bytes = b"".join(voiced_frames)
                        self._callback(audio_bytes)
                        voiced_frames = []
                        ring_buffer.clear()
                        triggered = False
