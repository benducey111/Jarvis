"""Animated AI orb — the visual centrepiece of Jarvis.

Draws entirely with QPainter: no external assets required.
A QTimer fires at ~60 fps to drive the animation tick.
"""

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import (
    QBrush, QColor, QPainter, QPainterPath, QPen, QRadialGradient,
)
from PyQt6.QtWidgets import QWidget

from core.state import AssistantState

# ---------------------------------------------------------------------------
# Colour palettes per state  (inner, mid, outer, ring)
# ---------------------------------------------------------------------------

_PALETTES = {
    AssistantState.IDLE: (
        QColor(140, 210, 255), QColor(50, 130, 255),
        QColor(20,  60, 180), QColor(80, 160, 255),
    ),
    AssistantState.LISTENING: (
        QColor(80,  220, 255), QColor(0,  150, 255),
        QColor(0,   60, 190), QColor(60, 200, 255),
    ),
    AssistantState.THINKING: (
        QColor(255, 200,  80), QColor(220, 130,  20),
        QColor(140,  70,   0), QColor(255, 170,  50),
    ),
    AssistantState.SPEAKING: (
        QColor(200, 110, 255), QColor(130,  40, 240),
        QColor( 60,  10, 160), QColor(170,  80, 255),
    ),
    AssistantState.CONFIRMING: (
        QColor(255, 200,  80), QColor(220, 130,  20),
        QColor(140,  70,   0), QColor(255, 170,  50),
    ),
    AssistantState.ERROR: (
        QColor(255, 100, 100), QColor(220,  40,  40),
        QColor(140,  10,  10), QColor(255,  80,  80),
    ),
}


class OrbWidget(QWidget):
    """Self-animating orb that reacts to AssistantState changes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(240, 240)

        self._state = AssistantState.IDLE
        self._tick = 0.0
        self._speak_intensity = 0.0   # 0–1, external or auto-decayed

        rng = random.Random(42)
        self._particles = [
            [
                rng.uniform(0, math.tau),          # angle
                rng.uniform(0.58, 0.90),           # orbit radius fraction
                rng.uniform(0.006, 0.022),         # angular speed
                rng.uniform(1.5, 4.5),             # dot size
                rng.uniform(0.35, 0.95),           # base alpha
            ]
            for _ in range(28)
        ]

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_frame)
        self._timer.start(16)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_state(self, state: AssistantState) -> None:
        self._state = state

    def set_speak_intensity(self, value: float) -> None:
        self._speak_intensity = max(0.0, min(1.0, value))

    # ------------------------------------------------------------------
    # Animation tick
    # ------------------------------------------------------------------

    def _tick_frame(self) -> None:
        state = self._state
        speeds = {
            AssistantState.SPEAKING:   0.065,
            AssistantState.LISTENING:  0.048,
            AssistantState.THINKING:   0.038,
            AssistantState.ERROR:      0.055,
        }
        self._tick += speeds.get(state, 0.020)

        if state != AssistantState.SPEAKING:
            self._speak_intensity *= 0.90

        particle_speed = 1.6 if state == AssistantState.SPEAKING else 1.0
        for p in self._particles:
            p[0] += p[2] * particle_speed

        self.update()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        t = self._tick
        state = self._state

        # ── Pulse multiplier ────────────────────────────────────────
        if state == AssistantState.SPEAKING:
            pulse = 1.0 + 0.16 * math.sin(t * 3.8) + self._speak_intensity * 0.10
            rot   = t * 1.9
            glow  = 1.65
        elif state == AssistantState.LISTENING:
            pulse = 1.0 + 0.07 * math.sin(t * 6.2)
            rot   = t * 1.3
            glow  = 1.30
        elif state == AssistantState.THINKING:
            pulse = 1.0 + 0.04 * math.sin(t * 2.6)
            rot   = t * 2.8
            glow  = 1.10
        elif state == AssistantState.ERROR:
            pulse = 1.0 + 0.09 * math.sin(t * 5.0)
            rot   = t * 0.6
            glow  = 1.05
        else:
            pulse = 1.0 + 0.032 * math.sin(t * 1.1)
            rot   = t * 0.55
            glow  = 0.85

        base_r = min(cx, cy) * 0.40
        r = base_r * pulse

        ci, cm, co, ring_c = _PALETTES.get(state, _PALETTES[AssistantState.IDLE])

        # ── 1. Ambient outer glow ────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(6, 0, -1):
            gr = r * (1.28 + 0.20 * i)
            alpha = int(18 * glow * (7 - i) / 6)
            c = QColor(ring_c)
            c.setAlpha(alpha)
            painter.setBrush(c)
            painter.drawEllipse(QPointF(cx, cy), gr, gr)

        # ── 2. Rotating energy rings ─────────────────────────────────
        n_rings = 3 if state == AssistantState.SPEAKING else 2
        for i in range(n_rings):
            rr = r * (1.16 + 0.15 * i)
            alpha = max(0, int(90 - 22 * i))
            c = QColor(ring_c); c.setAlpha(alpha)
            pen = QPen(c, 1.0, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(math.degrees(rot) + i * 55)
            painter.drawEllipse(QPointF(0, 0), rr, rr)
            painter.restore()

        # ── 3. Core orb (radial gradient sphere) ────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        grad = QRadialGradient(cx - r * 0.26, cy - r * 0.30, r * 1.45)
        c_i = QColor(ci); c_i.setAlpha(245)
        c_m = QColor(cm); c_m.setAlpha(225)
        c_o = QColor(co); c_o.setAlpha(205)
        c_b = QColor(co); c_b.setAlpha(0)
        grad.setColorAt(0.00, c_i)
        grad.setColorAt(0.35, c_m)
        grad.setColorAt(0.72, c_o)
        grad.setColorAt(1.00, c_b)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        # ── 4. Inner specular highlight ──────────────────────────────
        hr = r * 0.30
        hgrad = QRadialGradient(cx - hr * 0.28, cy - hr * 0.28, hr * 1.6)
        hgrad.setColorAt(0.0, QColor(255, 255, 255, 210))
        hgrad.setColorAt(0.5, QColor(ci.red(), ci.green(), ci.blue(), 100))
        hgrad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(hgrad))
        painter.drawEllipse(
            QPointF(cx - hr * 0.12, cy - hr * 0.18), hr, hr
        )

        # ── 5. Orbiting particles ────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self._particles:
            angle, rad_frac, _spd, size, alpha_base = p
            pr = r * rad_frac
            px = cx + pr * math.cos(angle)
            py = cy + pr * math.sin(angle)
            pc = QColor(ring_c)
            pc.setAlpha(int(alpha_base * 255 * min(1.0, glow * 0.65)))
            painter.setBrush(pc)
            hs = size * 0.5
            painter.drawEllipse(QPointF(px, py), hs, hs)

        # ── 6. Listening waveform ring ───────────────────────────────
        if state == AssistantState.LISTENING:
            self._draw_wave_ring(painter, cx, cy, r * 1.30, t, ring_c)

        # ── 7. Thinking scan line ────────────────────────────────────
        if state == AssistantState.THINKING:
            self._draw_scan(painter, cx, cy, r, t, ring_c)

        painter.end()

    # ------------------------------------------------------------------

    def _draw_wave_ring(self, p: QPainter, cx: float, cy: float,
                        radius: float, t: float, color: QColor) -> None:
        segs = 128
        path = QPainterPath()
        for i in range(segs + 1):
            frac  = i / segs
            angle = frac * math.tau
            wave  = (1.0
                     + 0.075 * math.sin(angle * 8  + t * 4.5)
                     + 0.038 * math.sin(angle * 16 + t * 8.0))
            rr = radius * wave
            px = cx + rr * math.cos(angle)
            py = cy + rr * math.sin(angle)
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)
        path.closeSubpath()
        wc = QColor(color); wc.setAlpha(95)
        p.setPen(QPen(wc, 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

    def _draw_scan(self, p: QPainter, cx: float, cy: float,
                   r: float, t: float, color: QColor) -> None:
        angle = t * 2.5
        x1 = cx + r * 1.2 * math.cos(angle)
        y1 = cy + r * 1.2 * math.sin(angle)
        x2 = cx + r * 1.2 * math.cos(angle + math.pi)
        y2 = cy + r * 1.2 * math.sin(angle + math.pi)
        sc = QColor(color); sc.setAlpha(55)
        p.setPen(QPen(sc, 1.0))
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
