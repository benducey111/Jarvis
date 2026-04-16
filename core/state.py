"""Assistant state enumeration."""

from enum import Enum, auto


class AssistantState(Enum):
    """All possible states the assistant pipeline can be in."""

    IDLE = auto()         # Ready and waiting for input
    LISTENING = auto()    # Microphone active, recording user speech
    THINKING = auto()     # Processing STT result / calling AI / dispatching command
    SPEAKING = auto()     # TTS audio is playing
    CONFIRMING = auto()   # Waiting for user to confirm/deny a safety-gated action
    ERROR = auto()        # An error occurred; displayed to user
