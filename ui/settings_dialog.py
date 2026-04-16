"""Settings dialog for runtime configuration changes."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from config.schema import Settings


class SettingsDialog(QDialog):
    """Modal dialog to change key settings without restarting.

    Signals:
        settings_changed(Settings): Emitted with updated settings when accepted.
    """

    settings_changed = pyqtSignal(object)

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Jarvis Settings")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._settings = settings
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── AI ────────────────────────────────────────────────────
        ai_group = QGroupBox("AI Backend")
        ai_form = QFormLayout(ai_group)

        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["openai", "ollama"])
        self.backend_combo.setCurrentText(self._settings.ai.backend)
        ai_form.addRow("Backend:", self.backend_combo)

        self.model_input = QLineEdit(self._settings.ai.model)
        ai_form.addRow("OpenAI Model:", self.model_input)

        self.ollama_model_input = QLineEdit(self._settings.ai.ollama_model)
        ai_form.addRow("Ollama Model:", self.ollama_model_input)

        layout.addWidget(ai_group)

        # ── TTS ───────────────────────────────────────────────────
        tts_group = QGroupBox("Voice (TTS)")
        tts_form = QFormLayout(tts_group)

        self.tts_backend_combo = QComboBox()
        self.tts_backend_combo.addItems(["edge_tts", "pyttsx3"])
        self.tts_backend_combo.setCurrentText(self._settings.tts.backend)
        tts_form.addRow("TTS Backend:", self.tts_backend_combo)

        self.voice_input = QLineEdit(self._settings.tts.voice)
        tts_form.addRow("Edge-TTS Voice:", self.voice_input)

        layout.addWidget(tts_group)

        # ── Safety ────────────────────────────────────────────────
        safety_group = QGroupBox("Safety")
        safety_form = QFormLayout(safety_group)

        self.safe_mode_check = QCheckBox("Enable safe mode")
        self.safe_mode_check.setChecked(self._settings.safety.safe_mode)
        safety_form.addRow(self.safe_mode_check)

        self.confirm_typing_check = QCheckBox("Confirm before typing")
        self.confirm_typing_check.setChecked(self._settings.safety.confirm_typing)
        safety_form.addRow(self.confirm_typing_check)

        layout.addWidget(safety_group)

        # ── Buttons ───────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        # Apply changes to a copy of settings
        s = self._settings
        s.ai.backend = self.backend_combo.currentText()
        s.ai.model = self.model_input.text().strip() or s.ai.model
        s.ai.ollama_model = self.ollama_model_input.text().strip() or s.ai.ollama_model
        s.tts.backend = self.tts_backend_combo.currentText()
        s.tts.voice = self.voice_input.text().strip() or s.tts.voice
        s.safety.safe_mode = self.safe_mode_check.isChecked()
        s.safety.confirm_typing = self.confirm_typing_check.isChecked()

        self.settings_changed.emit(s)
        self.accept()
