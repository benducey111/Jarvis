"""Status indicator widget showing the current assistant state."""

from PyQt6.QtCore import QPropertyAnimation, QRect, Qt, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from core.state import AssistantState
from ui.styles import STATUS_COLORS


class _PulsingDot(QWidget):
    """A small circle that pulses when the assistant is active."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._color = QColor(STATUS_COLORS["IDLE"])
        self._opacity = 1.0

    # Qt property for animation
    @pyqtProperty(float)
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        self._opacity = value
        self.update()

    def set_color(self, hex_color: str) -> None:
        self._color = QColor(hex_color)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self._color)
        color.setAlphaF(self._opacity)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(1, 1, 10, 10)


class StatusIndicator(QWidget):
    """Displays the current AssistantState as a coloured dot + label."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_state = AssistantState.IDLE
        self._animation: QPropertyAnimation | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._dot = _PulsingDot()
        self._label = QLabel("IDLE")
        self._label.setObjectName("statusLabel")

        layout.addWidget(self._dot)
        layout.addWidget(self._label)

    def update_state(self, state: AssistantState) -> None:
        """Update the indicator to reflect the new assistant state."""
        self._current_state = state
        name = state.name
        color = STATUS_COLORS.get(name, STATUS_COLORS["IDLE"])

        self._dot.set_color(color)
        self._label.setText(name)
        self._label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")

        self._stop_animation()

        if state in (AssistantState.LISTENING, AssistantState.THINKING,
                     AssistantState.SPEAKING):
            self._start_pulse()

    def _start_pulse(self) -> None:
        anim = QPropertyAnimation(self._dot, b"opacity")
        anim.setDuration(900)
        anim.setStartValue(1.0)
        anim.setEndValue(0.25)
        anim.setLoopCount(-1)           # infinite
        anim.start()
        self._animation = anim

    def _stop_animation(self) -> None:
        if self._animation:
            self._animation.stop()
            self._animation = None
        self._dot.opacity = 1.0
