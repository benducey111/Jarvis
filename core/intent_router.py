"""Intent router — classifies user input as a command or free-chat AI request."""

from loguru import logger


class IntentRouter:
    """Routes transcribed text to either the CommandRegistry or the AI backend.

    Routing logic:
    1. Normalise input (lowercase, strip punctuation).
    2. Try CommandRegistry.dispatch() — O(n) prefix match on all triggers.
    3. If a command is found, return ("command", command, args).
    4. Otherwise, return ("chat", None, original_text).
    """

    def __init__(self):
        # Import lazily to avoid circular imports at module load time
        from commands import registry
        self._registry = registry

    def route(self, text: str) -> tuple[str, object, str]:
        """Classify and route user input.

        Args:
            text: Raw transcribed or typed user input.

        Returns:
            Tuple of (route_type, command_or_none, args_or_text) where:
                route_type is "command" or "chat"
                command_or_none is the matched Command instance or None
                args_or_text is the argument string for a command,
                              or the original text for chat
        """
        if not text.strip():
            return "chat", None, text

        normalized = self._normalize(text)
        command, args = self._registry.dispatch(normalized)

        if command is not None:
            logger.debug(f"IntentRouter: command '{command.name}' matched | args='{args}'")
            return "command", command, args

        logger.debug(f"IntentRouter: no command match, routing to AI chat")
        return "chat", None, text

    @staticmethod
    def _normalize(text: str) -> str:
        """Lowercase and strip leading/trailing punctuation and whitespace."""
        # Keep internal punctuation (for e.g. URL recognition), just normalise edges
        return text.lower().strip().rstrip(".,!?")
