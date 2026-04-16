"""Jarvis — Windows AI Assistant entry point.

Startup sequence:
    1. Bootstrap logging (loguru)
    2. Load and validate configuration (YAML + .env)
    3. Create QApplication
    4. Instantiate JarvisWindow (applies dark theme, builds UI)
    5. Create PipelineWorker (QThread) and wire signals to window slots
    6. Start the worker thread (loads STT model, TTS, AI backend)
    7. Enter Qt event loop
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so all imports resolve
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Logging — set up before any other import so all modules can use loguru
# ---------------------------------------------------------------------------
from loguru import logger


def _configure_logging(log_file: str = "logs/jarvis.log",
                        level: str = "INFO",
                        rotation: str = "5 MB",
                        retention: str = "10 days") -> None:
    logger.remove()  # Remove default handler
    # Console handler (colourised)
    logger.add(
        sys.stdout,
        level=level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>"
        ),
    )
    # File handler (rotating)
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_file,
        level=level,
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
    )


_configure_logging()

# ---------------------------------------------------------------------------
# Qt high-DPI policy (must be set before QApplication is created)
# ---------------------------------------------------------------------------
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
from config import load_settings

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
from ui.main_window import JarvisWindow

# ---------------------------------------------------------------------------
# Pipeline worker
# ---------------------------------------------------------------------------
from core.assistant import PipelineWorker


def main() -> int:
    logger.info("=" * 60)
    logger.info("Jarvis starting up…")
    logger.info("=" * 60)

    # ── Load configuration ──────────────────────────────────────────
    settings = load_settings()
    _configure_logging(
        log_file=settings.logging.log_file,
        level=settings.logging.level,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
    )

    # ── Qt Application ──────────────────────────────────────────────
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis")
    app.setApplicationDisplayName("Jarvis AI Assistant")

    # ── Main window ─────────────────────────────────────────────────
    window = JarvisWindow(settings)
    window.show()

    # ── Pipeline worker ─────────────────────────────────────────────
    worker = PipelineWorker(settings)
    window._pipeline_worker = worker  # allow settings dialog to call update_settings

    # Wire worker signals → window slots (QueuedConnection across threads)
    worker.state_changed.connect(window.on_state_changed)
    worker.user_text_ready.connect(window.on_user_text)
    worker.assistant_text_ready.connect(window.on_assistant_text)
    worker.token_received.connect(window.on_token_received)
    worker.error_occurred.connect(window.on_error)
    worker.confirmation_required.connect(window.on_confirmation_required)

    # Wire UI signals → worker engine slots
    window.control_bar.text_submitted.connect(
        lambda text: worker.engine.handle_text_input(text)
        if worker.engine else None
    )
    window.control_bar.ptt_pressed.connect(
        lambda: worker.engine.start_listening()
        if worker.engine else None
    )
    window.control_bar.ptt_released.connect(
        lambda: worker.engine.stop_listening()
        if worker.engine else None
    )

    # Start the pipeline (loads models in the background)
    worker.start()
    logger.info("PipelineWorker started")

    # ── Graceful shutdown ───────────────────────────────────────────
    app.aboutToQuit.connect(worker.stop)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
