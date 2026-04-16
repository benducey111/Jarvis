"""Audio utility helpers for the Jarvis STT pipeline."""

import io

import numpy as np


def pcm16le_to_float32(audio_bytes: bytes, sample_rate: int = 16000) -> np.ndarray:
    """Convert raw 16-bit little-endian PCM bytes to float32 numpy array.

    faster-whisper expects a float32 array normalised to [-1.0, 1.0].

    Args:
        audio_bytes: Raw PCM bytes from sounddevice.
        sample_rate:  Sample rate (must match STT config, typically 16000).

    Returns:
        float32 ndarray, shape (num_samples,).
    """
    audio = np.frombuffer(audio_bytes, dtype=np.int16)
    return audio.astype(np.float32) / 32768.0


def float32_to_pcm16le(audio: np.ndarray) -> bytes:
    """Convert float32 numpy array back to raw PCM16LE bytes."""
    clamped = np.clip(audio, -1.0, 1.0)
    return (clamped * 32767).astype(np.int16).tobytes()


def pcm_to_wav_bytes(audio_bytes: bytes, sample_rate: int = 16000,
                     channels: int = 1) -> bytes:
    """Wrap raw PCM bytes in a valid WAV container.

    Useful when an API expects a WAV file rather than raw PCM.
    """
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)             # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    return buf.getvalue()
