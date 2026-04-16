"""Message bubble widget for the chat interface."""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.styles import COLOR_TEXT_SECONDARY


class MessageBubble(QFrame):
    """A single chat message displayed as a styled bubble.

    Args:
        text:      Message content.
        role:      "user" | "assistant" | "error"
        timestamp: Optional datetime; defaults to now.
    """

    def __init__(self, text: str, role: str = "assistant",
                 timestamp: datetime | None = None, parent=None):
        super().__init__(parent)
        self.role = role
        self._full_text = text

        self.setObjectName(
            "userBubble" if role == "user"
            else "errorBubble" if role == "error"
            else "assistantBubble"
        )

        self._build_layout(text, timestamp or datetime.now())

    def _build_layout(self, text: str, ts: datetime) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        bubble_frame = QFrame()
        bubble_frame.setObjectName(self.objectName())

        inner = QVBoxLayout(bubble_frame)
        inner.setContentsMargins(12, 10, 12, 10)
        inner.setSpacing(4)

        # Message text
        self._text_label = QLabel(text)
        self._text_label.setWordWrap(True)
        self._text_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._text_label.setObjectName("messageText")
        inner.addWidget(self._text_label)

        # Timestamp
        time_str = ts.strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 10px;")
        time_label.setObjectName("timestampLabel")

        if self.role == "user":
            time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            outer.addStretch()
            inner.addWidget(time_label)
            outer.addWidget(bubble_frame)
        else:
            time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            inner.addWidget(time_label)
            outer.addWidget(bubble_frame)
            outer.addStretch()

        # Constrain bubble width to ~75% of parent
        bubble_frame.setMaximumWidth(360)

    def append_text(self, token: str) -> None:
        """Append a streaming token to the message text."""
        self._full_text += token
        self._text_label.setText(self._full_text)

    def set_text(self, text: str) -> None:
        """Replace the full message text."""
        self._full_text = text
        self._text_label.setText(text)
