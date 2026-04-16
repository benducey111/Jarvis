"""Dark theme Qt stylesheet for Jarvis.

All visual styling is centralised here.  Fonts, colours, and widget shapes
are defined as constants so they can be referenced programmatically too.
"""

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

COLOR_BG_DARKEST = "#0d0d0f"          # Window / deepest background
COLOR_BG_DARK = "#141418"             # Main panel background
COLOR_BG_MID = "#1c1c22"             # Card / bubble background
COLOR_BG_LIGHT = "#25252e"           # Input field, hover states
COLOR_BORDER = "#2e2e3a"             # Subtle divider lines
COLOR_ACCENT = "#4f8ef7"             # Blue accent (buttons, active states)
COLOR_ACCENT_HOVER = "#6aa0ff"       # Button hover
COLOR_ACCENT_PRESSED = "#3a72d4"     # Button pressed
COLOR_TEXT_PRIMARY = "#e8e8f0"       # Main text
COLOR_TEXT_SECONDARY = "#8888a0"     # Timestamps, labels
COLOR_TEXT_MUTED = "#55556a"         # Placeholder text
COLOR_USER_BUBBLE = "#1e2d4a"        # User message bubble background
COLOR_ASSISTANT_BUBBLE = "#1a1a24"   # Assistant message bubble background
COLOR_SUCCESS = "#3dba6f"            # Success green
COLOR_WARNING = "#e8a930"            # Warning amber
COLOR_ERROR = "#e84545"              # Error red

# Status indicator colours per state
STATUS_COLORS = {
    "IDLE":       "#3dba6f",   # Green — ready
    "LISTENING":  "#4f8ef7",   # Blue — recording
    "THINKING":   "#e8a930",   # Amber — processing
    "SPEAKING":   "#a45ef7",   # Purple — talking
    "CONFIRMING": "#e8a930",   # Amber — waiting for user
    "ERROR":      "#e84545",   # Red — error
}

# ---------------------------------------------------------------------------
# Full dark theme QSS
# ---------------------------------------------------------------------------

DARK_THEME_QSS = f"""
/* ── Global ─────────────────────────────────────────────────────── */
QWidget {{
    background-color: {COLOR_BG_DARK};
    color: {COLOR_TEXT_PRIMARY};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    selection-background-color: {COLOR_ACCENT};
    selection-color: #ffffff;
}}

QMainWindow {{
    background-color: {COLOR_BG_DARKEST};
}}

/* ── Scroll areas ─────────────────────────────────────────────── */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: {COLOR_BG_DARKEST};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_MUTED};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    height: 0;   /* hide horizontal scrollbar */
}}

/* ── Text input ───────────────────────────────────────────────── */
QLineEdit {{
    background-color: {COLOR_BG_LIGHT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLOR_TEXT_PRIMARY};
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {COLOR_ACCENT};
}}
QLineEdit::placeholder {{
    color: {COLOR_TEXT_MUTED};
}}

QTextEdit {{
    background-color: {COLOR_BG_LIGHT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px;
    color: {COLOR_TEXT_PRIMARY};
}}
QTextEdit:focus {{
    border: 1px solid {COLOR_ACCENT};
}}

/* ── Buttons ──────────────────────────────────────────────────── */
QPushButton {{
    background-color: {COLOR_BG_LIGHT};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {COLOR_ACCENT};
    border-color: {COLOR_ACCENT};
    color: #ffffff;
}}
QPushButton:pressed {{
    background-color: {COLOR_ACCENT_PRESSED};
    border-color: {COLOR_ACCENT_PRESSED};
}}
QPushButton:disabled {{
    color: {COLOR_TEXT_MUTED};
    background-color: {COLOR_BG_MID};
    border-color: {COLOR_BG_MID};
}}

/* ── Push-to-talk button (objectName="pttButton") ─────────────── */
QPushButton#pttButton {{
    background-color: {COLOR_ACCENT};
    color: white;
    border: none;
    border-radius: 28px;
    font-size: 14px;
    font-weight: 600;
    min-width: 56px;
    min-height: 56px;
    max-width: 56px;
    max-height: 56px;
}}
QPushButton#pttButton:hover {{
    background-color: {COLOR_ACCENT_HOVER};
}}
QPushButton#pttButton:pressed {{
    background-color: {COLOR_ACCENT_PRESSED};
}}
QPushButton#pttButton[listening="true"] {{
    background-color: {COLOR_ERROR};
}}

/* ── Labels ───────────────────────────────────────────────────── */
QLabel {{
    background-color: transparent;
    color: {COLOR_TEXT_PRIMARY};
}}
QLabel#titleLabel {{
    font-size: 18px;
    font-weight: 700;
    color: {COLOR_TEXT_PRIMARY};
    letter-spacing: 1px;
}}
QLabel#statusLabel {{
    font-size: 11px;
    font-weight: 500;
    color: {COLOR_TEXT_SECONDARY};
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
QLabel#subtitleLabel {{
    font-size: 11px;
    color: {COLOR_TEXT_SECONDARY};
}}

/* ── Frames / containers ──────────────────────────────────────── */
QFrame#headerFrame {{
    background-color: {COLOR_BG_DARKEST};
    border-bottom: 1px solid {COLOR_BORDER};
}}
QFrame#controlBar {{
    background-color: {COLOR_BG_DARKEST};
    border-top: 1px solid {COLOR_BORDER};
}}
QFrame#chatContainer {{
    background-color: {COLOR_BG_DARK};
    border: none;
}}

/* ── Message bubbles ──────────────────────────────────────────── */
QFrame#userBubble {{
    background-color: {COLOR_USER_BUBBLE};
    border-radius: 12px;
    border-bottom-right-radius: 3px;
}}
QFrame#assistantBubble {{
    background-color: {COLOR_ASSISTANT_BUBBLE};
    border-radius: 12px;
    border-bottom-left-radius: 3px;
}}
QFrame#errorBubble {{
    background-color: #2a1515;
    border-radius: 12px;
    border: 1px solid {COLOR_ERROR};
}}

/* ── Separator ────────────────────────────────────────────────── */
QFrame[frameShape="4"],  /* HLine */
QFrame[frameShape="5"]   /* VLine */ {{
    color: {COLOR_BORDER};
    background-color: {COLOR_BORDER};
}}

/* ── Dialogs ──────────────────────────────────────────────────── */
QDialog {{
    background-color: {COLOR_BG_DARK};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}

/* ── Combo boxes ──────────────────────────────────────────────── */
QComboBox {{
    background-color: {COLOR_BG_LIGHT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    color: {COLOR_TEXT_PRIMARY};
}}
QComboBox:hover {{
    border-color: {COLOR_ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_BG_LIGHT};
    border: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: {COLOR_ACCENT};
}}

/* ── Check boxes ──────────────────────────────────────────────── */
QCheckBox {{
    spacing: 8px;
    color: {COLOR_TEXT_PRIMARY};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {COLOR_BORDER};
    background-color: {COLOR_BG_LIGHT};
}}
QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT};
    border-color: {COLOR_ACCENT};
}}

/* ── Tool tips ────────────────────────────────────────────────── */
QToolTip {{
    background-color: {COLOR_BG_LIGHT};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}}
"""
