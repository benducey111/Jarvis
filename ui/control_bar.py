"""Control bar — text input, push-to-talk, settings."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from core.state import AssistantState


class ControlBar(QWidget):
    """Bottom bar: text input + PTT mic button + settings gear.

    Signals
    -------
    text_submitted(str)   User pressed Enter or Send.
    ptt_pressed()         PTT button pressed down.
    ptt_released()        PTT button released.
    settings_requested()  Gear button clicked.
    """

    text_submitted    = pyqtSignal(str)
    ptt_pressed       = pyqtSignal()
    ptt_released      = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("controlBar")
        self.setFixedHeight(80)
        self._is_listening = False
        self._build_layout()

    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 8, 14, 10)
        root.setSpacing(0)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Command or question…")
        self.text_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.text_input.setFixedHeight(44)
        self.text_input.returnPressed.connect(self._submit)
        row.addWidget(self.text_input)

        # PTT mic button
        self.ptt_button = QPushButton("🎙")
        self.ptt_button.setObjectName("pttButton")
        self.ptt_button.setToolTip("Hold to speak")
        self.ptt_button.pressed.connect(self._on_pressed)
        self.ptt_button.released.connect(self._on_released)
        row.addWidget(self.ptt_button)

        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Settings")
        settings_btn.setFixedSize(44, 44)
        settings_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #1a2a50; "
            "  border-radius: 22px; font-size: 16px; color: #4a6890; }"
            "QPushButton:hover { border-color: #00b4ff; color: #00b4ff; }"
        )
        settings_btn.clicked.connect(self.settings_requested)
        row.addWidget(settings_btn)

        root.addLayout(row)

    # ------------------------------------------------------------------

    def _submit(self) -> None:
        text = self.text_input.text().strip()
        if text:
            self.text_input.clear()
            self.text_submitted.emit(text)

    def _on_pressed(self) -> None:
        self._is_listening = True
        self.ptt_button.setProperty("listening", "true")
        self.ptt_button.style().unpolish(self.ptt_button)
        self.ptt_button.style().polish(self.ptt_button)
        self.ptt_button.setText("⏹")
        self.ptt_pressed.emit()

    def _on_released(self) -> None:
        self._is_listening = False
        self.ptt_button.setProperty("listening", "false")
        self.ptt_button.style().unpolish(self.ptt_button)
        self.ptt_button.style().polish(self.ptt_button)
        self.ptt_button.setText("🎙")
        self.ptt_released.emit()

    def update_state(self, state: AssistantState) -> None:
        busy = state not in (AssistantState.IDLE, AssistantState.ERROR)
        self.text_input.setEnabled(
            not busy or state == AssistantState.CONFIRMING
        )
        if state != AssistantState.LISTENING and self._is_listening:
            self._is_listening = False
            self.ptt_button.setProperty("listening", "false")
            self.ptt_button.style().unpolish(self.ptt_button)
            self.ptt_button.style().polish(self.ptt_button)
            self.ptt_button.setText("🎙")
