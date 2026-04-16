# Jarvis — Windows AI Assistant

A production-quality desktop AI assistant for Windows with voice control, a modern dark-theme UI, and a modular command system.

---

## Features

- **Voice input** — Push-to-talk via faster-whisper (runs locally, no cloud STT)
- **Voice output** — Microsoft neural voices via edge-tts (free, requires internet); pyttsx3 offline fallback
- **AI responses** — GPT-4o-mini via OpenAI API (or swap to local Ollama)
- **Command system** — Open apps, search Google, type text, open folders, control volume, take screenshots
- **Safety system** — Confirmation prompts for risky actions; safe mode toggle
- **Dark theme UI** — Modern chat interface built with PyQt6
- **Extensible** — Plugin system, config-based app shortcuts, swappable AI/STT/TTS backends

---

## Setup

### 1. Prerequisites

- Python 3.11 or 3.12 (64-bit)
- Windows 10 or 11
- An OpenAI API key (or [Ollama](https://ollama.ai) installed for local AI)

### 2. Clone and install

```bash
git clone https://github.com/benducey111/Jarvis.git
cd Jarvis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `webrtcvad-wheels` provides pre-built binaries — no C compiler needed.

### 3. Configure your API key

```bash
copy .env.example .env
```

Edit `.env` and add your key:

```
OPENAI_API_KEY=sk-...your-key-here...
```

### 4. Run

```bash
python main.py
```

The first launch downloads the faster-whisper `base.en` model (~140 MB). Subsequent launches are instant.

---

## Configuration

### `config/settings.yaml`

| Setting | Default | Description |
|---|---|---|
| `ai.backend` | `openai` | `openai` or `ollama` |
| `ai.model` | `gpt-4o-mini` | OpenAI model name |
| `stt.model_size` | `base.en` | Whisper model: `tiny.en`, `base.en`, `small.en` |
| `tts.voice` | `en-US-GuyNeural` | Edge-TTS voice (see voices below) |
| `safety.safe_mode` | `true` | Require confirmation for risky commands |

### Adding apps and websites (`config/apps.yaml`)

```yaml
apps:
  - name: My App
    path: "C:\\Path\\To\\App.exe"
    aliases: [my app, my application]

websites:
  - name: My Site
    url: "https://example.com"
    aliases: [my site, example]
```

### Using Ollama (local AI, no API key needed)

1. Install [Ollama](https://ollama.ai)
2. Run `ollama pull llama3`
3. Edit `config/settings.yaml`: set `ai.backend: ollama`

### Changing the TTS voice

Popular edge-tts voices:

| Voice ID | Description |
|---|---|
| `en-US-GuyNeural` | US English male (default) |
| `en-US-AriaNeural` | US English female |
| `en-GB-RyanNeural` | British English male |
| `en-GB-SoniaNeural` | British English female |

List all available voices: `edge-tts --list-voices`

---

## Voice Commands

| Say... | Action |
|---|---|
| `open chrome` | Launch Chrome |
| `open discord` | Launch Discord |
| `search for Python tutorials` | Google search |
| `type hello world` | Type text into active window |
| `open downloads` | Open Downloads folder |
| `screenshot` | Save screenshot to Desktop |
| `volume up` / `volume down` | Adjust system volume |
| `mute` / `unmute` | Mute/unmute audio |
| `what time is it` | Tell current time |
| `what's today` | Tell current date |
| `clear history` | Reset conversation |
| `enable safe mode` | Require confirmation for risky actions |
| `disable safe mode` | Skip confirmation prompts |
| `help` | List all commands |

---

## Project Structure

```
Jarvis/
├── main.py              # Entry point
├── config/              # Settings, app shortcuts, Pydantic schema
├── core/                # AssistantEngine, state machine, safety gate
├── services/            # STT, TTS, AI backend implementations
│   ├── stt/             # faster-whisper + microphone capture
│   ├── tts/             # edge-tts + pyttsx3 fallback
│   └── ai/              # OpenAI + Ollama backends
├── commands/            # Modular command handlers (auto-registered)
├── ui/                  # PyQt6 widgets (dark theme, chat, controls)
├── utils/               # Audio helpers, text processing, Windows utils
├── plugins/             # Drop-in custom commands (auto-loaded)
└── logs/                # Rotating log files
```

---

## Adding Custom Commands (Plugins)

Create a file in `plugins/` that inherits from `commands.base.Command`:

```python
# plugins/my_command.py
from commands.base import Command, CommandResult
import commands as _cmd_pkg

class MyCommand(Command):
    name = "my command"
    aliases = ["do my thing"]
    description = "Does my custom thing."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        return CommandResult(success=True, response="Done!")

_cmd_pkg.registry.register(MyCommand())
```

Restart Jarvis — your command is automatically loaded.

---

## Troubleshooting

**`portaudio` / microphone errors** — sounddevice bundles its own PortAudio. If you still see errors, try: `pip install sounddevice --force-reinstall`

**`faster-whisper` slow on first run** — The model downloads on first use. Subsequent runs load from cache (~140 MB).

**edge-tts no audio** — Requires internet. Falls back to pyttsx3 automatically if offline.

**OpenAI `AuthenticationError`** — Check `.env` has a valid `OPENAI_API_KEY`.

---

## V2 Upgrade Ideas

- **Wake word** (`pvporcupine` or `openwakeword`) — always-on "Hey Jarvis"
- **Screen understanding** (`PIL.ImageGrab` + vision model) — "what's on my screen?"
- **File search** — Natural language search over local files
- **Persistent memory** — Long-term user preferences and context
- **Routines** — "gaming mode" / "focus mode" that chains multiple commands
- **System tray mode** — Hide to tray, global hotkey to summon
- **Streaming voice output** — Sub-200ms first-word latency

---

## License

MIT
