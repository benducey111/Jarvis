"""Scrollable chat history widget."""

from datetime import datetime

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QFrame, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from ui.message_bubble import MessageBubble


class ChatWidget(QWidget):
    """Scrollable list of MessageBubble widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatContainer")
        self._last_assistant: MessageBubble | None = None
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._content = QWidget()
        self._content.setObjectName("chatContainer")
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)
        self._layout.addStretch()

        self._scroll.setWidget(self._content)
        root.addWidget(self._scroll)

    # ------------------------------------------------------------------

    def add_user_message(self, text: str,
                         timestamp: datetime | None = None) -> None:
        self._last_assistant = None
        self._insert(MessageBubble(text, role="user", timestamp=timestamp))

    def add_assistant_message(self, text: str = "",
                              timestamp: datetime | None = None) -> "MessageBubble":
        bubble = MessageBubble(text, role="assistant", timestamp=timestamp)
        self._last_assistant = bubble
        self._insert(bubble)
        return bubble

    def add_error_message(self, text: str) -> None:
        self._last_assistant = None
        self._insert(MessageBubble(text, role="error"))

    def append_to_last_assistant(self, token: str) -> None:
        if self._last_assistant is None:
            self._last_assistant = self.add_assistant_message("")
        self._last_assistant.append_text(token)
        self._scroll_bottom()

    def clear(self) -> None:
        self._last_assistant = None
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_divider(self) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._insert_widget(line)

    # ------------------------------------------------------------------

    def _insert(self, bubble: MessageBubble) -> None:
        self._insert_widget(bubble)

    def _insert_widget(self, widget: QWidget) -> None:
        self._layout.insertWidget(self._layout.count() - 1, widget)
        self._scroll_bottom()

    def _scroll_bottom(self) -> None:
        QTimer.singleShot(
            50,
            lambda: self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()
            ),
        )
