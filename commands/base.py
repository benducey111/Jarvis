"""Base classes for all Jarvis commands."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CommandResult:
    """Returned by every command execution."""

    success: bool
    response: str                    # Text shown in UI and spoken by TTS
    speak: bool = True               # Whether TTS should voice this response
    data: dict = field(default_factory=dict)  # Optional extra data for the engine


class Command(ABC):
    """Abstract base for all Jarvis commands.

    Subclasses must define:
        name: str                     - canonical command name
        aliases: list[str]            - trigger phrases (lowercase)
        description: str              - shown in help
        requires_confirmation: bool   - if True, SafetyGate may pause execution
        confirmation_message: str     - shown to user when confirmation required
    """

    name: str = ""
    aliases: list[str] = []
    description: str = ""
    requires_confirmation: bool = False
    confirmation_message: str = "Are you sure you want to do this?"

    @abstractmethod
    def execute(self, args: str) -> CommandResult:
        """Execute the command.

        Args:
            args: Everything from the user's input after the matched trigger phrase.

        Returns:
            CommandResult
        """
        ...

    def __repr__(self) -> str:
        return f"<Command name={self.name!r} aliases={self.aliases}>"
