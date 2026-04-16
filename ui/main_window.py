"""Main application window — futuristic frameless HUD design."""

import math
import random
from datetime import datetime

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import (
    QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen,
)
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from config.schema import Settings
from core.state import AssistantState
from ui.chat_widget import ChatWidget
from ui.control_bar import ControlBar
from ui.orb_widget import OrbWidget
from ui.settings_dialog import SettingsDialog
from ui.styles import (
    COLOR_ACCENT, COLOR_BG_DARK, COLOR_BG_VOID,
    COLOR_BORDER_GLOW, COLOR_TEXT_SECONDARY,
    DARK_THEME_QSS,
)


# ---------------------------------------------------------------------------
# Animated background canvas
# ---------------------------------------------------------------------------

class _Background(QWidget):
    """Particle-network background; transparent to mouse events."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        rng = random.Random(7)
        self._particles = [
            {
                "x": rng.random(), "y": rng.random(),
                "vx": rng.uniform(-0.00012, 0.00012),
                "vy": rng.uniform(-0.00012, 0.00012),
                "r": rng.uniform(1.2, 2.8),
                "a": rng.uniform(0.25, 0.70),
            }
            for _ in range(38)
        ]
        self._tick = 0.0
        t = QTimer(self)
        t.timeout.connect(self._step)
        t.start(50)

    def _step(self) -> None:
        self._tick += 0.015
        for p in self._particles:
            p["x"] = (p["x"] + p["vx"]) % 1.0
            p["y"] = (p["y"] + p["vy"]) % 1.0
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(COLOR_BG_VOID))
        grad.setColorAt(1.0, QColor(COLOR_BG_DARK))
        painter.fillRect(0, 0, w, h, QBrush(grad))

        pen = QPen(QColor(30, 55, 110, 18), 1)
        painter.setPen(pen)
        for x in range(0, w, 55):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, 55):
            painter.drawLine(0, y, w, y)

        painter.setPen(Qt.PenStyle.NoPen)
        pts = [(p["x"] * w, p["y"] * h) for p in self._particles]
        for i, p in enumerate(self._particles):
            px, py = pts[i]
            c = QColor(60, 140, 255, int(p["a"] * 210))
            painter.setBrush(c)
            painter.drawEllipse(QPointF(px, py), p["r"], p["r"])

        for i, (x1, y1) in enumerate(pts):
            for x2, y2 in pts[i + 1:]:
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < 110:
                    alpha = int(38 * (1 - dist / 110))
                    painter.setPen(QPen(QColor(60, 120, 255, alpha), 1))
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        painter.end()


# ---------------------------------------------------------------------------
# Draggable title bar
# ---------------------------------------------------------------------------

class _TitleBar(QWidget):
    def __init__(self, win: "JarvisWindow"):
        super().__init__(win)
        self._win = win
        self._drag_pos = None
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 12, 0)
        layout.setSpacing(10)

        dot = QLabel("◈")
        dot.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 14px;")
        layout.addWidget(dot)

        title = QLabel("JARVIS")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        sub = QLabel("A.I. SYSTEM")
        sub.setObjectName("subtitleLabel")
        layout.addWidget(sub)

        layout.addStretch()

        self._clock = QLabel()
        self._clock.setObjectName("clockLabel")
        layout.addWidget(self._clock)
        layout.addSpacing(8)

        btn_css = (
            "QPushButton { background: transparent; border: none; "
            f" color: {COLOR_TEXT_SECONDARY}; font-size: 14px; "
            " min-width: 28px; max-width: 28px; "
            " min-height: 28px; max-height: 28px; border-radius: 14px; }"
            "QPushButton:hover { background: rgba(255,255,255,15); color: #ffffff; }"
        )

        min_btn = QPushButton("—")
        min_btn.setStyleSheet(btn_css)
        min_btn.setCursor(Qt.CursorShape.ArrowCursor)
        min_btn.clicked.connect(win.showMinimized)
        layout.addWidget(min_btn)

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(
            btn_css + "QPushButton:hover { background: rgba(255,50,50,180); color: white; }"
        )
        close_btn.setCursor(Qt.CursorShape.ArrowCursor)
        close_btn.clicked.connect(win.close)
        layout.addWidget(close_btn)

        ct = QTimer(self)
        ct.timeout.connect(self._tick_clock)
        ct.start(1000)
        self._tick_clock()

    def _tick_clock(self) -> None:
        self._clock.setText(datetime.now().strftime("%H:%M:%S"))

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self._win.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self._win.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802
        self._drag_pos = None

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setPen(QPen(QColor(COLOR_BORDER_GLOW), 1))
        p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        p.end()


# ---------------------------------------------------------------------------
# Status strip
# ---------------------------------------------------------------------------

class _StatusRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(26)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

        self._dot = QLabel("●")
        self._label = QLabel("READY")
        self._dot.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 8px;")
        self._label.setStyleSheet(
            f"color: {COLOR_ACCENT}; font-size: 10px; font-weight: 600; letter-spacing: 2px;"
        )
        layout.addWidget(self._dot)
        layout.addSpacing(5)
        layout.addWidget(self._label)
        layout.addStretch()

    def update_state(self, state: AssistantState) -> None:
        from ui.styles import STATUS_COLORS
        color = STATUS_COLORS.get(state.name, COLOR_ACCENT)
        labels = {
            "IDLE": "READY", "LISTENING": "LISTENING",
            "THINKING": "THINKING", "SPEAKING": "SPEAKING",
            "CONFIRMING": "CONFIRM?", "ERROR": "ERROR",
        }
        self._dot.setStyleSheet(f"color: {color}; font-size: 8px;")
        self._label.setText(labels.get(state.name, state.name))
        self._label.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: 600; letter-spacing: 2px;"
        )


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class JarvisWindow(QWidget):
    """Frameless futuristic HUD window."""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._pipeline_worker = None

        self.setWindowTitle("Jarvis")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 820)
        self.setMinimumSize(420, 600)

        if settings.ui.stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.setStyleSheet(DARK_THEME_QSS)
        self._build_ui()

    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._bg = _Background(self)
        self._bg.setGeometry(self.rect())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._title_bar = _TitleBar(self)
        root.addWidget(self._title_bar)

        # Orb section
        orb_wrap = QWidget()
        orb_wrap.setFixedHeight(290)
        ol = QVBoxLayout(orb_wrap)
        ol.setContentsMargins(0, 4, 0, 4)
        ol.setSpacing(0)

        self._status_row = _StatusRow()
        ol.addWidget(self._status_row)

        self.orb = OrbWidget()
        self.orb.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        ol.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(orb_wrap)

        # Chat glass panel
        chat_outer = QWidget()
        chat_outer.setObjectName("chatOuter")
        co_layout = QVBoxLayout(chat_outer)
        co_layout.setContentsMargins(0, 0, 0, 0)
        self.chat = ChatWidget()
        co_layout.addWidget(self.chat)

        chat_wrapper = QWidget()
        cw_layout = QVBoxLayout(chat_wrapper)
        cw_layout.setContentsMargins(10, 0, 10, 6)
        cw_layout.addWidget(chat_outer)
        root.addWidget(chat_wrapper, stretch=1)

        self.control_bar = ControlBar()
        self.control_bar.settings_requested.connect(self._open_settings)
        root.addWidget(self.control_bar)

        self.chat.add_assistant_message(
            "Systems online. I'm Jarvis — hold the mic button to speak, "
            "or type below."
        )

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._bg.setGeometry(self.rect())

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 16, 16)
        painter.setPen(QPen(QColor(COLOR_BORDER_GLOW), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.end()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @pyqtSlot(object)
    def on_state_changed(self, state: AssistantState) -> None:
        self.orb.set_state(state)
        self._status_row.update_state(state)
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
        reply = QMessageBox.question(
            self, "Confirm Action", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        callback(reply == QMessageBox.StandardButton.Yes)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._settings, parent=self)
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    @pyqtSlot(object)
    def _apply_settings(self, settings: Settings) -> None:
        self._settings = settings
        if self._pipeline_worker and hasattr(self._pipeline_worker, "update_settings"):
            self._pipeline_worker.update_settings(settings)
