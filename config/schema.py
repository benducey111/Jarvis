"""Pydantic v2 configuration schema.

All application settings are validated through these models on startup.
API keys are loaded from environment variables / .env file and never
stored in settings.yaml.
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class AIConfig(BaseModel):
    backend: str = "openai"          # "openai" | "ollama"
    model: str = "gpt-4o-mini"       # model name passed to the backend
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3"
    system_prompt: str = (
        "You are Jarvis, a helpful and concise personal AI assistant for Windows. "
        "Keep your responses brief and conversational. "
        "When the user asks you to perform computer tasks, confirm what you're doing."
    )
    max_history_messages: int = 20   # sliding window size (pairs)
    temperature: float = 0.7
    max_tokens: int = 512


class STTConfig(BaseModel):
    backend: str = "faster_whisper"  # "faster_whisper" | "google"
    model_size: str = "base.en"      # faster-whisper model: tiny.en, base.en, small.en
    device: str = "cpu"              # "cpu" | "cuda"
    compute_type: str = "int8"       # "int8" | "float16" | "float32"
    language: str = "en"
    vad_aggressiveness: int = 2      # webrtcvad: 0 (lenient) – 3 (aggressive)
    silence_threshold_ms: int = 800  # ms of silence before ending recording
    sample_rate: int = 16000
    channels: int = 1


class TTSConfig(BaseModel):
    backend: str = "edge_tts"        # "edge_tts" | "pyttsx3"
    voice: str = "en-US-GuyNeural"   # edge-tts voice name
    rate: str = "+0%"                # edge-tts speed adjustment e.g. "+10%", "-5%"
    volume: str = "+0%"              # edge-tts volume adjustment
    pyttsx3_rate: int = 185          # pyttsx3 words per minute


class UIConfig(BaseModel):
    window_width: int = 480
    window_height: int = 720
    font_family: str = "Segoe UI"
    font_size: int = 13
    frameless: bool = False          # Set True for borderless HUD window (Phase 5)
    stay_on_top: bool = False
    minimize_to_tray: bool = False


class SafetyConfig(BaseModel):
    safe_mode: bool = True           # Require confirmation for risky commands
    confirm_typing: bool = True      # Require confirmation before typing text
    confirm_shell: bool = True       # Require confirmation before running shell commands


class LoggingConfig(BaseModel):
    level: str = "INFO"              # DEBUG | INFO | WARNING | ERROR
    log_file: str = "logs/jarvis.log"
    rotation: str = "5 MB"
    retention: str = "10 days"


# ---------------------------------------------------------------------------
# App / Web shortcut entries (from apps.yaml)
# ---------------------------------------------------------------------------


class AppEntry(BaseModel):
    name: str
    path: str = ""                   # Executable path (for desktop apps)
    url: str = ""                    # URL (for web shortcuts)
    aliases: list[str] = Field(default_factory=list)

    def is_web(self) -> bool:
        return bool(self.url)


# ---------------------------------------------------------------------------
# Root settings model (reads from environment + .env)
# ---------------------------------------------------------------------------


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # API keys (from environment / .env only — never in YAML)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # Sub-configs (loaded from YAML separately and merged)
    ai: AIConfig = Field(default_factory=AIConfig)
    stt: STTConfig = Field(default_factory=STTConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
