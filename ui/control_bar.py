"""Control bar: push-to-talk button, status indicator, text input."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.state import AssistantState
from ui.status_indicator import StatusIndicator


class ControlBar(QWidget):
    """Bottom bar containing the text input, PTT button, and status indicator.

    Signals:
        text_submitted(str):   User submitted text via Enter or Send button.
        ptt_pressed():         Push-to-talk button pressed down.
        ptt_released():        Push-to-talk button released.
        settings_requested():  Settings gear button clicked.
    """

    text_submitted = pyqtSignal(str)
    ptt_pressed = pyqtSignal()
    ptt_released = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("controlBar")
        self.setFixedHeight(100)
        self._is_listening = False
        self._build_layout()

    def _build_layout(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 12)
        root.setSpacing(8)

        # ── Status row ────────────────────────────────────────────
        status_row = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        status_row.addWidget(self.status_indicator)
        status_row.addStretch()

        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Settings")
        settings_btn.setFixedSize(28, 28)
        settings_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "font-size: 16px; color: #8888a0; }"
            "QPushButton:hover { color: #e8e8f0; }"
        )
        settings_btn.clicked.connect(self.settings_requested)
        status_row.addWidget(settings_btn)

        root.addLayout(status_row)

        # ── Input row ─────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a message or press mic to speak…")
        self.text_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.text_input.setFixedHeight(40)
        self.text_input.returnPressed.connect(self._on_text_submitted)
        input_row.addWidget(self.text_input)

        # Push-to-talk mic button
        self.ptt_button = QPushButton("🎙")
        self.ptt_button.setObjectName("pttButton")
        self.ptt_button.setToolTip("Hold to speak (Push-to-Talk)")
        self.ptt_button.pressed.connect(self._on_ptt_pressed)
        self.ptt_button.released.connect(self._on_ptt_released)
        input_row.addWidget(self.ptt_button)

        root.addLayout(input_row)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_text_submitted(self) -> None:
        text = self.text_input.text().strip()
        if text:
            self.text_input.clear()
            self.text_submitted.emit(text)

    def _on_ptt_pressed(self) -> None:
        self._is_listening = True
        self.ptt_button.setProperty("listening", "true")
        self.ptt_button.setStyle(self.ptt_button.style())  # force style refresh
        self.ptt_button.setText("⏹")
        self.ptt_pressed.emit()

    def _on_ptt_released(self) -> None:
        self._is_listening = False
        self.ptt_button.setProperty("listening", "false")
        self.ptt_button.setStyle(self.ptt_button.style())
        self.ptt_button.setText("🎙")
        self.ptt_released.emit()

    def update_state(self, state: AssistantState) -> None:
        """Reflect the assistant state in the control bar."""
        self.status_indicator.update_state(state)
        is_busy = state not in (AssistantState.IDLE, AssistantState.ERROR)
        self.text_input.setEnabled(not is_busy or state == AssistantState.CONFIRMING)
        if state != AssistantState.LISTENING:
            # Ensure PTT button resets if state changed externally
            if self._is_listening:
                self._is_listening = False
                self.ptt_button.setProperty("listening", "false")
                self.ptt_button.setStyle(self.ptt_button.style())
                self.ptt_button.setText("🎙")
