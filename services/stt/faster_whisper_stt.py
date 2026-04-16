"""Faster-Whisper speech-to-text service."""

from loguru import logger

from services.stt.base import STTBase
from utils.audio_utils import pcm16le_to_float32


class FasterWhisperSTT(STTBase):
    """Local STT using faster-whisper (CTranslate2-compiled Whisper).

    The model is loaded once at initialisation.  On Windows with a
    CPU-only setup, the int8 quantised 'base.en' model is recommended
    for a good speed/accuracy tradeoff.
    """

    def __init__(
        self,
        model_size: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
    ):
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._language = language
        self._model = None
        self._ready = False

        self._load_model()

    def _load_model(self) -> None:
        try:
            from faster_whisper import WhisperModel

            logger.info(
                f"Loading faster-whisper model '{self._model_size}' "
                f"(device={self._device}, compute_type={self._compute_type})…"
            )
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
            )
            self._ready = True
            logger.info("faster-whisper model loaded and ready.")
        except ImportError:
            logger.error(
                "faster-whisper not installed. Run: pip install faster-whisper"
            )
        except Exception as exc:
            logger.exception(f"Failed to load faster-whisper model: {exc}")

    def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe raw 16kHz mono PCM16LE audio bytes to text.

        Returns empty string on failure or if no speech detected.
        """
        if not self._ready or self._model is None:
            logger.warning("FasterWhisperSTT: model not ready, skipping transcription")
            return ""

        if len(audio_bytes) < 512:
            return ""  # Too short to contain speech

        try:
            audio_float32 = pcm16le_to_float32(audio_bytes)

            segments, info = self._model.transcribe(
                audio_float32,
                language=self._language,
                beam_size=5,
                vad_filter=True,        # built-in VAD to skip non-speech
                vad_parameters={"min_silence_duration_ms": 300},
            )

            text = " ".join(segment.text for segment in segments).strip()
            if text:
                logger.debug(f"STT transcript: '{text}'")
            return text

        except Exception as exc:
            logger.exception(f"Transcription failed: {exc}")
            return ""

    def is_ready(self) -> bool:
        return self._ready
