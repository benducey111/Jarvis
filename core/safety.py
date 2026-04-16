"""Safety gate for command execution.

All commands pass through SafetyGate before being executed.
Commands that declare requires_confirmation=True will be held
in CONFIRMING state until the user explicitly approves or denies.
"""

from enum import Enum, auto
from loguru import logger


class SafetyDecision(Enum):
    ALLOW = auto()
    REQUIRE_CONFIRM = auto()
    DENY = auto()


class SafetyGate:
    """Centralized safety checker inserted between intent routing and command execution."""

    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        logger.debug(f"SafetyGate initialized | safe_mode={safe_mode}")

    def check(self, command, args: str = "") -> SafetyDecision:
        """Decide whether a command can execute immediately or needs confirmation.

        Args:
            command: A Command instance (must have requires_confirmation attribute).
            args: The argument string passed to the command (for logging).

        Returns:
            SafetyDecision
        """
        if not command.requires_confirmation:
            return SafetyDecision.ALLOW

        if self.safe_mode:
            logger.info(
                f"SafetyGate: REQUIRE_CONFIRM for '{command.name}' "
                f"(safe_mode=True, args='{args}')"
            )
            return SafetyDecision.REQUIRE_CONFIRM

        # safe_mode is off — allow even confirmation-required commands
        logger.warning(
            f"SafetyGate: ALLOW (safe_mode=False) for '{command.name}' | args='{args}'"
        )
        return SafetyDecision.ALLOW

    def set_safe_mode(self, enabled: bool) -> None:
        self.safe_mode = enabled
        logger.info(f"SafetyGate: safe_mode set to {enabled}")
