"""Status indicator — kept for backwards compatibility; not used in HUD layout."""

from PyQt6.QtCore import QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from core.state import AssistantState
from ui.styles import STATUS_COLORS


class _Dot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self._color = QColor(STATUS_COLORS["IDLE"])
        self._opacity = 1.0

    @pyqtProperty(float)
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, v: float) -> None:
        self._opacity = v
        self.update()

    def set_color(self, hex_color: str) -> None:
        self._color = QColor(hex_color)
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self._color)
        c.setAlphaF(self._opacity)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(1, 1, 8, 8)


class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anim: QPropertyAnimation | None = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self._dot = _Dot()
        self._label = QLabel("IDLE")
        self._label.setObjectName("statusLabel")
        layout.addWidget(self._dot)
        layout.addWidget(self._label)

    def update_state(self, state: AssistantState) -> None:
        color = STATUS_COLORS.get(state.name, STATUS_COLORS["IDLE"])
        self._dot.set_color(color)
        self._label.setText(state.name)
        self._label.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: 600; letter-spacing: 1px;"
        )
        self._stop()
        if state in (AssistantState.LISTENING, AssistantState.THINKING,
                     AssistantState.SPEAKING):
            self._pulse()

    def _pulse(self) -> None:
        a = QPropertyAnimation(self._dot, b"opacity")
        a.setDuration(850)
        a.setStartValue(1.0)
        a.setEndValue(0.2)
        a.setLoopCount(-1)
        a.start()
        self._anim = a

    def _stop(self) -> None:
        if self._anim:
            self._anim.stop()
            self._anim = None
        self._dot.opacity = 1.0
