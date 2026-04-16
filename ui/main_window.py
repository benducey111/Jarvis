"""Main application window for Jarvis."""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from config.schema import Settings
from core.state import AssistantState
from ui.chat_widget import ChatWidget
from ui.control_bar import ControlBar
from ui.settings_dialog import SettingsDialog
from ui.styles import COLOR_ACCENT, DARK_THEME_QSS


class JarvisWindow(QMainWindow):
    """Top-level application window.

    Responsibilities:
    - Assemble header, chat area, and control bar
    - Apply dark theme stylesheet
    - Connect UI signals to the pipeline worker (wired from main.py)
    - Receive and display pipeline signals (state changes, messages, errors)
    """

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings

        self.setWindowTitle("Jarvis")
        self.resize(settings.ui.window_width, settings.ui.window_height)
        self.setMinimumSize(380, 500)

        if settings.ui.stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # Apply the global dark stylesheet
        self.setStyleSheet(DARK_THEME_QSS)

        self._build_ui()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        self.chat = ChatWidget()
        root.addWidget(self.chat, stretch=1)

        self.control_bar = ControlBar()
        self.control_bar.settings_requested.connect(self._open_settings)
        root.addWidget(self.control_bar)

        # Show a welcome message
        self.chat.add_assistant_message(
            "Hello! I'm Jarvis. Press the mic button to speak, "
            "or type below. How can I help you?"
        )

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)

        # Accent dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 10px;")

        title = QLabel("JARVIS")
        title.setObjectName("titleLabel")

        subtitle = QLabel("Personal AI Assistant")
        subtitle.setObjectName("subtitleLabel")

        layout.addWidget(dot)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(subtitle)
        layout.addStretch()

        return header

    # ------------------------------------------------------------------
    # Public slots — called by PipelineWorker signals
    # ------------------------------------------------------------------

    @pyqtSlot(object)
    def on_state_changed(self, state: AssistantState) -> None:
        self.control_bar.update_state(state)

    @pyqtSlot(str)
    def on_user_text(self, text: str) -> None:
        self.chat.add_user_message(text)

    @pyqtSlot(str)
    def on_assistant_text(self, text: str) -> None:
        self.chat.add_assistant_message(text)

    @pyqtSlot(str)
    def on_token_received(self, token: str) -> None:
        self.chat.append_to_last_assistant(token)

    @pyqtSlot(str)
    def on_error(self, message: str) -> None:
        self.chat.add_error_message(f"Error: {message}")
        self.control_bar.update_state(AssistantState.ERROR)

    @pyqtSlot(str, object)
    def on_confirmation_required(self, message: str, callback) -> None:
        """Show a confirmation dialog.  Calls callback(True/False)."""
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        confirmed = reply == QMessageBox.StandardButton.Yes
        callback(confirmed)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._settings, parent=self)
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    @pyqtSlot(object)
    def _apply_settings(self, settings: Settings) -> None:
        self._settings = settings
        # Emit to pipeline worker if it exposes a settings_updated slot
        if hasattr(self, "_pipeline_worker") and self._pipeline_worker:
            if hasattr(self._pipeline_worker, "update_settings"):
                self._pipeline_worker.update_settings(settings)
