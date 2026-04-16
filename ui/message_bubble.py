"""Message bubble for the chat interface."""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.styles import COLOR_TEXT_SECONDARY


class MessageBubble(QFrame):
    """A single chat message rendered as a styled bubble.

    Parameters
    ----------
    text:      Message content.
    role:      "user" | "assistant" | "error"
    timestamp: Optional datetime (defaults to now).
    """

    def __init__(self, text: str, role: str = "assistant",
                 timestamp: datetime | None = None, parent=None):
        super().__init__(parent)
        self.role = role
        self._full_text = text

        self.setObjectName(
            "userBubble"      if role == "user"
            else "errorBubble" if role == "error"
            else "assistantBubble"
        )

        self._build(text, timestamp or datetime.now())

    def _build(self, text: str, ts: datetime) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setObjectName(self.objectName())

        inner = QVBoxLayout(frame)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(4)

        # Role badge (tiny, muted)
        if self.role == "assistant":
            badge = QLabel("JARVIS")
            badge.setStyleSheet(
                f"color: #7b2fff; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;"
            )
            inner.addWidget(badge)
        elif self.role == "user":
            badge = QLabel("YOU")
            badge.setStyleSheet(
                "color: #00b4ff; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;"
            )
            badge.setAlignment(Qt.AlignmentFlag.AlignRight)
            inner.addWidget(badge)

        self._text_label = QLabel(text)
        self._text_label.setWordWrap(True)
        self._text_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._text_label.setObjectName("messageText")
        inner.addWidget(self._text_label)

        time_label = QLabel(ts.strftime("%H:%M"))
        time_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 9px;"
        )

        if self.role == "user":
            time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            inner.addWidget(time_label)
            outer.addStretch()
            outer.addWidget(frame)
        else:
            inner.addWidget(time_label)
            outer.addWidget(frame)
            outer.addStretch()

        frame.setMaximumWidth(380)

    def append_text(self, token: str) -> None:
        self._full_text += token
        self._text_label.setText(self._full_text)

    def set_text(self, text: str) -> None:
        self._full_text = text
        self._text_label.setText(text)
