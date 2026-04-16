"""Futuristic dark theme for Jarvis — neon + glassmorphism palette.

All colours are defined as module-level constants so other widgets
can reference them programmatically (e.g. for QPainter drawing).
"""

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

COLOR_BG_VOID      = "#03050f"
COLOR_BG_DARK      = "#060a18"
COLOR_BG_PANEL     = "#0a1020"
COLOR_BG_INPUT     = "#0d1428"
COLOR_BG_HOVER     = "#131c38"
COLOR_BORDER       = "#1a2a50"
COLOR_BORDER_GLOW  = "#1e3d7a"

COLOR_ACCENT       = "#00b4ff"
COLOR_ACCENT2      = "#7b2fff"
COLOR_ACCENT3      = "#0066ff"
COLOR_ACCENT_HOVER = "#33c8ff"
COLOR_ACCENT_PRESS = "#0080cc"

COLOR_TEXT_PRIMARY   = "#c8deff"
COLOR_TEXT_SECONDARY = "#4a6890"
COLOR_TEXT_MUTED     = "#253448"

COLOR_USER_BUBBLE  = "#0a1e3a"
COLOR_ASST_BUBBLE  = "#080e20"

COLOR_SUCCESS = "#00e676"
COLOR_WARNING = "#ffab00"
COLOR_ERROR   = "#ff3d3d"

STATUS_COLORS = {
    "IDLE":       COLOR_SUCCESS,
    "LISTENING":  COLOR_ACCENT,
    "THINKING":   COLOR_WARNING,
    "SPEAKING":   COLOR_ACCENT2,
    "CONFIRMING": COLOR_WARNING,
    "ERROR":      COLOR_ERROR,
}

# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------

DARK_THEME_QSS = f"""
* {{
    font-family: "Segoe UI", "Inter", "SF Pro Display", sans-serif;
    font-size: 13px;
    color: {COLOR_TEXT_PRIMARY};
}}
QWidget {{
    background-color: transparent;
    selection-background-color: {COLOR_ACCENT};
    selection-color: #ffffff;
}}
QMainWindow, #rootFrame {{
    background-color: {COLOR_BG_DARK};
}}

QScrollArea {{ border: none; background-color: transparent; }}
QScrollBar:vertical {{
    background: transparent; width: 4px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_BORDER_GLOW}; border-radius: 2px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {COLOR_ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

QLineEdit {{
    background-color: {COLOR_BG_INPUT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    padding: 8px 14px;
    color: {COLOR_TEXT_PRIMARY};
}}
QLineEdit:focus {{
    border: 1px solid {COLOR_ACCENT};
    background-color: #0e1830;
}}

QPushButton {{
    background-color: {COLOR_BG_INPUT};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {COLOR_BG_HOVER};
    border-color: {COLOR_ACCENT};
    color: {COLOR_ACCENT};
}}
QPushButton:pressed {{
    background-color: {COLOR_ACCENT_PRESS};
    border-color: {COLOR_ACCENT_PRESS};
    color: #ffffff;
}}
QPushButton:disabled {{
    color: {COLOR_TEXT_MUTED};
    background-color: {COLOR_BG_PANEL};
    border-color: {COLOR_BORDER};
}}

QPushButton#pttButton {{
    background-color: {COLOR_ACCENT3};
    color: white;
    border: 2px solid {COLOR_ACCENT};
    border-radius: 30px;
    font-size: 20px;
    min-width: 60px; min-height: 60px;
    max-width: 60px; max-height: 60px;
}}
QPushButton#pttButton:hover {{
    background-color: {COLOR_ACCENT};
    border-color: {COLOR_ACCENT_HOVER};
}}
QPushButton#pttButton:pressed,
QPushButton#pttButton[listening="true"] {{
    background-color: {COLOR_ERROR};
    border-color: {COLOR_ERROR};
}}

QLabel {{ background-color: transparent; color: {COLOR_TEXT_PRIMARY}; }}
QLabel#titleLabel {{
    font-size: 20px; font-weight: 700;
    letter-spacing: 4px; color: {COLOR_ACCENT};
}}
QLabel#subtitleLabel {{
    font-size: 10px; letter-spacing: 2px; color: {COLOR_TEXT_SECONDARY};
}}
QLabel#statusLabel {{
    font-size: 10px; font-weight: 600; letter-spacing: 1.5px;
}}
QLabel#clockLabel {{
    font-size: 11px; color: {COLOR_TEXT_SECONDARY}; letter-spacing: 1px;
}}

QWidget#chatOuter {{
    background-color: rgba(8,14,28,215);
    border: 1px solid rgba(30,61,122,120);
    border-radius: 14px;
}}
QWidget#chatContainer {{ background-color: transparent; }}

QFrame#userBubble {{
    background-color: rgba(10,30,58,220);
    border: 1px solid rgba(0,180,255,60);
    border-radius: 14px;
    border-bottom-right-radius: 3px;
}}
QFrame#assistantBubble {{
    background-color: rgba(8,14,32,220);
    border: 1px solid rgba(123,47,255,50);
    border-radius: 14px;
    border-bottom-left-radius: 3px;
}}
QFrame#errorBubble {{
    background-color: rgba(40,8,8,220);
    border: 1px solid rgba(255,61,61,90);
    border-radius: 14px;
}}

QWidget#controlBar {{
    background-color: rgba(6,10,24,230);
    border-top: 1px solid rgba(30,61,122,100);
}}

QDialog {{
    background-color: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER_GLOW};
    border-radius: 14px;
}}
QGroupBox {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    margin-top: 8px; padding-top: 8px;
    color: {COLOR_TEXT_SECONDARY};
    font-size: 11px; font-weight: 600; letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 0 6px; color: {COLOR_ACCENT};
}}

QComboBox {{
    background-color: {COLOR_BG_INPUT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px; padding: 5px 10px;
    color: {COLOR_TEXT_PRIMARY};
}}
QComboBox:hover {{ border-color: {COLOR_ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background-color: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER_GLOW};
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: {COLOR_ACCENT3};
}}

QCheckBox {{ spacing: 8px; color: {COLOR_TEXT_PRIMARY}; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid {COLOR_BORDER};
    background-color: {COLOR_BG_INPUT};
}}
QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT3}; border-color: {COLOR_ACCENT};
}}

QToolTip {{
    background-color: {COLOR_BG_PANEL};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER_GLOW};
    padding: 4px 8px; border-radius: 6px; font-size: 11px;
}}

QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {COLOR_BORDER}; background-color: {COLOR_BORDER}; max-height: 1px;
}}
"""
