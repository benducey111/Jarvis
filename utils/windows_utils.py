"""Windows-specific utility helpers."""

import ctypes
import os
import subprocess
import sys
from pathlib import Path


def is_admin() -> bool:
    """Return True if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False  # Not on Windows


def get_foreground_window_title() -> str:
    """Return the title of the currently focused window.

    Returns empty string on failure or non-Windows platform.
    """
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def expand_env_path(path: str) -> str:
    """Expand environment variables in a Windows path string.

    Handles both %VAR% style (Windows) and $VAR style (Unix-like).
    """
    return os.path.expandvars(os.path.expanduser(path))


def open_path(path: str) -> bool:
    """Open a file, folder, or URL using its default Windows handler.

    Equivalent to double-clicking in Explorer.

    Returns:
        True on success, False on failure.
    """
    try:
        os.startfile(expand_env_path(path))
        return True
    except Exception:
        return False
