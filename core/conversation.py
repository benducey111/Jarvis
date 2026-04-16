"""Conversation history manager with sliding window and JSON persistence."""

import json
from pathlib import Path

from loguru import logger


class ConversationManager:
    """Manages the in-memory message history for the AI backend.

    Maintains a list in OpenAI message format:
        [{"role": "user" | "assistant" | "system", "content": "..."}]

    The system prompt is always prepended and never stored in the history list.
    History is trimmed to max_messages pairs to keep context windows manageable.
    """

    _HISTORY_FILE = Path("logs/conversation_history.json")

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self._system_prompt = system_prompt
        self._max_messages = max_messages  # max number of individual messages (not pairs)
        self._history: list[dict[str, str]] = []
        self._load_history()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_messages(self) -> list[dict[str, str]]:
        """Return the full messages list (system prompt + history) for the AI backend."""
        return [{"role": "system", "content": self._system_prompt}] + self._history

    def append_user(self, text: str) -> None:
        self._history.append({"role": "user", "content": text})
        self._trim()

    def append_assistant(self, text: str) -> None:
        self._history.append({"role": "assistant", "content": text})
        self._trim()

    def clear(self) -> None:
        self._history.clear()
        logger.info("Conversation history cleared")

    def update_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_history(self) -> None:
        """Persist conversation history to disk."""
        try:
            self._HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self._HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            logger.debug(f"Conversation saved ({len(self._history)} messages)")
        except Exception as exc:
            logger.warning(f"Could not save conversation history: {exc}")

    def _load_history(self) -> None:
        if not self._HISTORY_FILE.exists():
            return
        try:
            with open(self._HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self._history = data[-self._max_messages:]
                logger.debug(f"Loaded {len(self._history)} messages from history")
        except Exception as exc:
            logger.warning(f"Could not load conversation history: {exc}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _trim(self) -> None:
        """Keep history within the sliding window limit."""
        if len(self._history) > self._max_messages:
            # Remove oldest messages two at a time (user+assistant pairs)
            trim_count = len(self._history) - self._max_messages
            self._history = self._history[trim_count:]
