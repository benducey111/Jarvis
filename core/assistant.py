"""AssistantEngine and PipelineWorker — the heart of Jarvis.

PipelineWorker runs the full STT → Intent → AI/Command → TTS pipeline
in a dedicated QThread so the Qt event loop (main thread) stays responsive.

All cross-thread communication uses Qt signals or asyncio.run_coroutine_threadsafe.
"""

import asyncio
import threading

from loguru import logger
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from config.schema import Settings
from core.conversation import ConversationManager
from core.intent_router import IntentRouter
from core.safety import SafetyDecision, SafetyGate
from core.state import AssistantState
from utils.text_utils import clean_for_tts, extract_sentence_boundary


class AssistantEngine(QObject):
    """Orchestrates the full assistant pipeline inside PipelineWorker's thread."""

    state_changed = pyqtSignal(object)
    user_text_ready = pyqtSignal(str)
    assistant_text_ready = pyqtSignal(str)
    token_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    confirmation_required = pyqtSignal(str, object)

    def __init__(self, settings: Settings, loop: asyncio.AbstractEventLoop,
                 parent=None):
        super().__init__(parent)
        self._settings = settings
        self._loop = loop          # The running event loop owned by PipelineWorker
        self._tts = None
        self._stt = None
        self._mic = None
        self._ai = None
        self._conversation: ConversationManager | None = None
        self._router: IntentRouter | None = None
        self._safety: SafetyGate | None = None
        self._ready = False

        self._confirm_event = threading.Event()
        self._confirm_result: bool = False

    # ------------------------------------------------------------------
    # Initialisation (called from PipelineWorker.run, inside the event loop)
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Load all services synchronously. Called from the worker thread."""
        logger.info("AssistantEngine: initialising services…")
        self._emit_state(AssistantState.THINKING)

        try:
            self._safety = SafetyGate(safe_mode=self._settings.safety.safe_mode)
            self._router = IntentRouter()
            self._conversation = ConversationManager(
                system_prompt=self._settings.ai.system_prompt,
                max_messages=self._settings.ai.max_history_messages,
            )
            self._init_stt()
            self._init_tts()
            self._init_ai()
            self._ready = True
            logger.info("AssistantEngine: ready.")
        except Exception as exc:
            logger.exception("AssistantEngine: initialisation failed")
            self.error_occurred.emit(f"Startup error: {exc}")
        finally:
            # Always return to IDLE so the UI becomes interactive
            self._emit_state(AssistantState.IDLE)

    def _init_stt(self) -> None:
        from services.stt.faster_whisper_stt import FasterWhisperSTT
        cfg = self._settings.stt
        self._stt = FasterWhisperSTT(
            model_size=cfg.model_size,
            device=cfg.device,
            compute_type=cfg.compute_type,
            language=cfg.language,
        )

    def _init_tts(self) -> None:
        cfg = self._settings.tts
        if cfg.backend == "pyttsx3":
            from services.tts.pyttsx3_service import Pyttsx3Service
            self._tts = Pyttsx3Service(rate=cfg.pyttsx3_rate)
        else:
            from services.tts.edge_tts_service import EdgeTTSService
            self._tts = EdgeTTSService(
                voice=cfg.voice, rate=cfg.rate, volume=cfg.volume
            )

    def _init_ai(self) -> None:
        cfg = self._settings.ai
        if cfg.backend == "ollama":
            from services.ai.ollama_backend import OllamaBackend
            self._ai = OllamaBackend(
                base_url=cfg.ollama_base_url,
                model=cfg.ollama_model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        else:
            from services.ai.openai_backend import OpenAIBackend
            self._ai = OpenAIBackend(
                api_key=self._settings.openai_api_key,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )

    # ------------------------------------------------------------------
    # Public entry points (called from main thread — thread-safe)
    # ------------------------------------------------------------------

    def submit_text(self, text: str) -> None:
        """Schedule text processing on the async event loop (thread-safe)."""
        if not self._ready or not text.strip():
            return
        asyncio.run_coroutine_threadsafe(self._process_text(text), self._loop)

    def start_listening(self) -> None:
        """Start microphone capture (thread-safe)."""
        if not self._ready:
            return
        if self._mic is None:
            from services.stt.microphone import MicrophoneCapture
            self._mic = MicrophoneCapture(
                on_audio_callback=self._on_audio_captured,
                sample_rate=self._settings.stt.sample_rate,
                vad_aggressiveness=self._settings.stt.vad_aggressiveness,
                silence_threshold_ms=self._settings.stt.silence_threshold_ms,
            )
        self._emit_state(AssistantState.LISTENING)
        self._mic.start_listening()

    def stop_listening(self) -> None:
        """Stop microphone capture and process whatever was recorded (thread-safe)."""
        if self._mic:
            self._mic.stop_listening()

    # ------------------------------------------------------------------
    # Audio → STT → pipeline
    # ------------------------------------------------------------------

    def _on_audio_captured(self, audio_bytes: bytes) -> None:
        """Called from MicrophoneCapture's thread when recording ends."""
        asyncio.run_coroutine_threadsafe(
            self._process_audio(audio_bytes), self._loop
        )

    async def _process_audio(self, audio_bytes: bytes) -> None:
        self._emit_state(AssistantState.THINKING)
        try:
            text = self._stt.transcribe(audio_bytes) if self._stt else ""
            if not text:
                logger.debug("STT returned empty transcript")
                self._emit_state(AssistantState.IDLE)
                return
            await self._process_text(text)
        except Exception as exc:
            logger.exception("Error processing audio")
            self.error_occurred.emit(str(exc))
            self._emit_state(AssistantState.ERROR)

    async def _process_text(self, text: str) -> None:
        """Core pipeline: intent → command/chat → TTS."""
        self.user_text_ready.emit(text)
        self._emit_state(AssistantState.THINKING)
        try:
            route_type, command, args = self._router.route(text)
            if route_type == "command":
                await self._execute_command(command, args)
            else:
                await self._run_chat(text)
        except Exception as exc:
            logger.exception("Pipeline error")
            self.error_occurred.emit(str(exc))
            self._emit_state(AssistantState.ERROR)

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------

    async def _execute_command(self, command, args: str) -> None:
        decision = self._safety.check(command, args)

        if decision == SafetyDecision.REQUIRE_CONFIRM:
            msg = command.confirmation_message.format(text=args or "")
            confirmed = await self._ask_confirmation(msg)
            if not confirmed:
                response = "Okay, cancelled."
                self.assistant_text_ready.emit(response)
                await self._speak(response)
                self._emit_state(AssistantState.IDLE)
                return

        result = command.execute(args)

        if result.data.get("action") == "clear_history":
            self._conversation.clear()
        elif result.data.get("action") == "set_safe_mode":
            self._safety.set_safe_mode(result.data["value"])
        elif result.data.get("action") == "stop_speaking":
            if self._tts:
                self._tts.stop()
            self._emit_state(AssistantState.IDLE)
            return

        if result.response:
            self.assistant_text_ready.emit(result.response)
            if result.speak:
                await self._speak(result.response)

        self._emit_state(AssistantState.IDLE)

    async def _ask_confirmation(self, message: str) -> bool:
        self._confirm_event.clear()
        self._confirm_result = False
        self._emit_state(AssistantState.CONFIRMING)
        self.confirmation_required.emit(message, self._on_confirmation_response)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._confirm_event.wait, 30)
        return self._confirm_result

    def _on_confirmation_response(self, confirmed: bool) -> None:
        self._confirm_result = confirmed
        self._confirm_event.set()

    # ------------------------------------------------------------------
    # AI chat
    # ------------------------------------------------------------------

    async def _run_chat(self, text: str) -> None:
        self._conversation.append_user(text)
        messages = self._conversation.build_messages()

        if not self._ai or not self._ai.is_available():
            fallback = (
                "I'm not connected to an AI backend. "
                "Please add your OPENAI_API_KEY to .env and restart."
            )
            self.assistant_text_ready.emit(fallback)
            await self._speak(fallback)
            self._emit_state(AssistantState.IDLE)
            return

        full_response = ""
        tts_buffer = ""

        try:
            async for token in self._ai.stream_chat(messages):
                full_response += token
                tts_buffer += token
                self.token_received.emit(token)

                sentence, tts_buffer = extract_sentence_boundary(tts_buffer)
                if sentence:
                    clean = clean_for_tts(sentence)
                    if clean:
                        # Create task on the current (running) loop — no loop= needed
                        self._loop.create_task(self._speak(clean))

            if tts_buffer.strip():
                self._loop.create_task(self._speak(clean_for_tts(tts_buffer)))

            self._conversation.append_assistant(full_response)
        except Exception as exc:
            logger.exception("Chat stream failed")
            self.error_occurred.emit(str(exc))

        self._emit_state(AssistantState.IDLE)

    # ------------------------------------------------------------------
    # TTS
    # ------------------------------------------------------------------

    async def _speak(self, text: str) -> None:
        if not self._tts or not text.strip():
            return
        self._emit_state(AssistantState.SPEAKING)
        try:
            await self._tts.speak(text)
        except Exception as exc:
            logger.exception(f"TTS failed: {exc}")
            try:
                from services.tts.pyttsx3_service import Pyttsx3Service
                fallback = Pyttsx3Service()
                await fallback.speak(text)
            except Exception:
                pass
        finally:
            self._emit_state(AssistantState.IDLE)

    # ------------------------------------------------------------------
    # Settings update
    # ------------------------------------------------------------------

    def update_settings(self, settings: Settings) -> None:
        self._settings = settings
        if self._safety:
            self._safety.set_safe_mode(settings.safety.safe_mode)
        if self._conversation:
            self._conversation.update_system_prompt(settings.ai.system_prompt)
        self._init_tts()
        logger.info("AssistantEngine: settings updated")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def shutdown(self) -> None:
        if self._mic:
            self._mic.stop_listening()
        if self._conversation:
            self._conversation.save_history()
        self._loop.call_soon_threadsafe(self._loop.stop)
        logger.info("AssistantEngine: shut down")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _emit_state(self, state: AssistantState) -> None:
        self.state_changed.emit(state)


# ---------------------------------------------------------------------------
# QThread wrapper
# ---------------------------------------------------------------------------


class PipelineWorker(QThread):
    """QThread that owns and runs the AssistantEngine."""

    state_changed = pyqtSignal(object)
    user_text_ready = pyqtSignal(str)
    assistant_text_ready = pyqtSignal(str)
    token_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    confirmation_required = pyqtSignal(str, object)

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.engine: AssistantEngine | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def run(self) -> None:
        """Entry point for the worker thread."""
        # Create the event loop FIRST so the engine gets a reference to it
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop

        # Create engine with the loop already set
        self.engine = AssistantEngine(self._settings, loop=loop)

        # Forward all engine signals to worker signals (QueuedConnection auto-used
        # because engine lives in this thread and connections cross to main thread)
        self.engine.state_changed.connect(self.state_changed)
        self.engine.user_text_ready.connect(self.user_text_ready)
        self.engine.assistant_text_ready.connect(self.assistant_text_ready)
        self.engine.token_received.connect(self.token_received)
        self.engine.error_occurred.connect(self.error_occurred)
        self.engine.confirmation_required.connect(self.confirmation_required)

        # Initialise services (synchronous: loads STT model, sets up TTS/AI)
        self.engine.initialize()

        # Run the event loop forever — all async tasks execute here
        loop.run_forever()

    def stop(self) -> None:
        if self.engine:
            self.engine.shutdown()
        else:
            if self._loop:
                self._loop.call_soon_threadsafe(self._loop.stop)
        self.quit()
        self.wait()
