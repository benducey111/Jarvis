"""Microphone capture with optional voice-activity detection.

Primary mode: Push-to-Talk (PTT).
  - start_listening()  → begin recording
  - stop_listening()   → emit all recorded audio, stop

Secondary mode (when webrtcvad is available): always-on VAD.
  - start_listening()  → continuously detect speech/silence
  - Audio is emitted automatically when silence follows speech

webrtcvad is OPTIONAL.  If it's not installed (Python 3.14 requires
MSVC to build it), PTT mode works perfectly without it.
"""

import threading
from collections import deque
from typing import Callable

from loguru import logger


# Minimum recorded audio length to bother sending to STT (avoids empty clips)
_MIN_AUDIO_BYTES = 16000 * 2 * 0.3  # 0.3 seconds of 16kHz 16-bit mono


class MicrophoneCapture:
    """Records microphone audio and emits chunks via a callback.

    PTT mode (default / VAD unavailable):
        Press → start_listening()
        Release → stop_listening()  ← emits all audio immediately

    VAD mode (when webrtcvad is installed):
        start_listening() keeps running; audio is emitted automatically
        when speech → silence transitions are detected.
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
        self._silence_frames = max(1, int(silence_threshold_ms / 30))  # 30ms frames

        self._stop_flag = threading.Event()
        self._flush_event = threading.Event()   # PTT release: emit now
        self._thread: threading.Thread | None = None

        # 30ms frame at 16kHz = 480 samples
        self._frame_duration_ms = 30
        self._frame_size = int(sample_rate * self._frame_duration_ms / 1000)

        self._vad = None  # lazily initialised (None = not yet tried)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_listening(self) -> None:
        """Begin microphone capture in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_flag.clear()
        self._flush_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.debug("MicrophoneCapture: started")

    def stop_listening(self) -> None:
        """Stop capture.

        Flushes any accumulated audio before stopping so PTT always
        gets a transcription even when VAD is unavailable.
        """
        self._flush_event.set()   # signal the loop to emit immediately
        self._stop_flag.set()
        if self._thread:
            self._thread.join(timeout=3)
        self._thread = None
        logger.debug("MicrophoneCapture: stopped")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _get_vad(self):
        """Lazily try to load webrtcvad.  Returns Vad instance or False."""
        if self._vad is None:
            try:
                import webrtcvad
                self._vad = webrtcvad.Vad(self._vad_aggressiveness)
                logger.debug("webrtcvad loaded — VAD-assisted mode active")
            except ImportError:
                logger.info(
                    "webrtcvad not installed — running in PTT-only mode. "
                    "(Optional: pip install webrtcvad-wheels for always-on VAD)"
                )
                self._vad = False  # sentinel: don't try again
        return self._vad

    def _capture_loop(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("sounddevice not installed. Run: pip install sounddevice")
            return

        vad = self._get_vad()
        vad_active = vad is not False and vad is not None

        ring_buffer: deque = deque(maxlen=self._silence_frames)
        voiced_frames: list[bytes] = []
        triggered = False

        mode = "VAD" if vad_active else "PTT"
        logger.info(f"MicrophoneCapture: listening at {self._sample_rate}Hz [{mode} mode]")

        try:
            with sd.RawInputStream(
                samplerate=self._sample_rate,
                blocksize=self._frame_size,
                channels=self._channels,
                dtype="int16",
            ) as stream:
                while not self._stop_flag.is_set():

                    # ── PTT flush: emit immediately and exit ──────────
                    if self._flush_event.is_set():
                        if voiced_frames:
                            audio_bytes = b"".join(voiced_frames)
                            if len(audio_bytes) >= _MIN_AUDIO_BYTES:
                                logger.debug(
                                    f"MicrophoneCapture: PTT flush, "
                                    f"emitting {len(voiced_frames)} frames"
                                )
                                self._callback(audio_bytes)
                            else:
                                logger.debug("MicrophoneCapture: audio too short, skipping")
                        break

                    # ── Read one 30ms frame ───────────────────────────
                    raw_bytes, overflowed = stream.read(self._frame_size)
                    frame = bytes(raw_bytes)

                    if vad_active:
                        # ── VAD mode: detect speech / silence transitions ──
                        try:
                            is_speech = vad.is_speech(frame, self._sample_rate)
                        except Exception:
                            is_speech = True

                        if not triggered:
                            ring_buffer.append((frame, is_speech))
                            num_voiced = sum(1 for _, s in ring_buffer if s)
                            if num_voiced > 0.6 * ring_buffer.maxlen:
                                triggered = True
                                voiced_frames.extend(f for f, _ in ring_buffer)
                                ring_buffer.clear()
                                logger.debug("MicrophoneCapture: speech onset detected")
                        else:
                            voiced_frames.append(frame)
                            ring_buffer.append((frame, is_speech))
                            num_unvoiced = sum(1 for _, s in ring_buffer if not s)
                            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                                audio_bytes = b"".join(voiced_frames)
                                if len(audio_bytes) >= _MIN_AUDIO_BYTES:
                                    logger.debug(
                                        f"MicrophoneCapture: silence, "
                                        f"emitting {len(voiced_frames)} frames"
                                    )
                                    self._callback(audio_bytes)
                                voiced_frames = []
                                ring_buffer.clear()
                                triggered = False
                    else:
                        # ── PTT mode: just accumulate all frames ─────────
                        voiced_frames.append(frame)

        except Exception as exc:
            logger.exception(f"MicrophoneCapture error: {exc}")
