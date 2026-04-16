"""Scrollable chat history widget."""

from datetime import datetime

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.message_bubble import MessageBubble


class ChatWidget(QWidget):
    """Scrollable list of MessageBubble widgets.

    New messages are appended at the bottom.  The view auto-scrolls to the
    latest message unless the user has manually scrolled up.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatContainer")

        # Track the last assistant bubble for streaming updates
        self._last_assistant_bubble: MessageBubble | None = None

        self._build_layout()

    def _build_layout(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self._content = QWidget()
        self._content.setObjectName("chatContainer")
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(8)
        self._layout.addStretch()   # pushes messages to bottom initially

        self._scroll.setWidget(self._content)
        root.addWidget(self._scroll)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_user_message(self, text: str,
                         timestamp: datetime | None = None) -> None:
        """Append a user message bubble."""
        self._last_assistant_bubble = None
        self._insert_bubble(MessageBubble(text, role="user", timestamp=timestamp))

    def add_assistant_message(self, text: str = "",
                              timestamp: datetime | None = None) -> MessageBubble:
        """Append an assistant message bubble and return it (for streaming)."""
        bubble = MessageBubble(text, role="assistant", timestamp=timestamp)
        self._last_assistant_bubble = bubble
        self._insert_bubble(bubble)
        return bubble

    def add_error_message(self, text: str) -> None:
        """Append an error bubble."""
        self._last_assistant_bubble = None
        self._insert_bubble(MessageBubble(text, role="error"))

    def append_to_last_assistant(self, token: str) -> None:
        """Append a streaming token to the most recent assistant bubble.

        If no assistant bubble exists yet, creates one.
        """
        if self._last_assistant_bubble is None:
            self._last_assistant_bubble = self.add_assistant_message("")
        self._last_assistant_bubble.append_text(token)
        self._scroll_to_bottom()

    def clear(self) -> None:
        """Remove all message bubbles."""
        self._last_assistant_bubble = None
        while self._layout.count() > 1:   # keep the trailing stretch
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_divider(self) -> None:
        """Insert a thin horizontal divider (e.g. between sessions)."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._insert_widget(line)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _insert_bubble(self, bubble: MessageBubble) -> None:
        self._insert_widget(bubble)

    def _insert_widget(self, widget: QWidget) -> None:
        # Insert before the trailing stretch (last item)
        insert_pos = self._layout.count() - 1
        self._layout.insertWidget(insert_pos, widget)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom after the layout has updated."""
        QTimer.singleShot(
            50,
            lambda: self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()
            ),
        )
