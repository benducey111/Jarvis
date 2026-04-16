"""System control commands: volume, screenshot, clipboard."""

import datetime
import subprocess

from loguru import logger

import commands as _cmd_pkg
from commands.base import Command, CommandResult


class VolumeCommand(Command):
    name = "volume"
    aliases = [
        "set volume", "volume up", "volume down",
        "mute", "unmute", "increase volume", "decrease volume",
    ]
    description = "Adjust system volume. E.g. 'volume up', 'mute'"
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        action = args.lower().strip()
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            if "mute" in action:
                volume.SetMute(1, None)
                return CommandResult(success=True, response="Muted.")
            elif "unmute" in action:
                volume.SetMute(0, None)
                return CommandResult(success=True, response="Unmuted.")
            elif "up" in action or "increase" in action:
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
                return CommandResult(success=True, response="Volume increased.")
            elif "down" in action or "decrease" in action:
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
                return CommandResult(success=True, response="Volume decreased.")
            else:
                return CommandResult(success=False, response="Say 'volume up', 'volume down', 'mute', or 'unmute'.")

        except ImportError:
            return CommandResult(
                success=False,
                response="pycaw is not installed. Run: pip install pycaw comtypes",
            )
        except Exception as exc:
            logger.exception("VolumeCommand failed")
            return CommandResult(success=False, response=f"Volume control failed: {exc}")


class ScreenshotCommand(Command):
    name = "screenshot"
    aliases = ["take screenshot", "take a screenshot", "capture screen", "capture"]
    description = "Take a screenshot and save it to the Desktop."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        try:
            from PIL import ImageGrab
            import os

            desktop = os.path.expandvars(r"%USERPROFILE%\Desktop")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(desktop, f"screenshot_{timestamp}.png")

            img = ImageGrab.grab()
            img.save(path)
            logger.info(f"Screenshot saved: {path}")
            return CommandResult(success=True, response=f"Screenshot saved to Desktop.")
        except ImportError:
            return CommandResult(
                success=False,
                response="Pillow is not installed. Run: pip install Pillow",
            )
        except Exception as exc:
            logger.exception("ScreenshotCommand failed")
            return CommandResult(success=False, response=f"Screenshot failed: {exc}")


class ClipboardCommand(Command):
    name = "copy to clipboard"
    aliases = ["clipboard", "copy"]
    description = "Copy text to the clipboard. E.g. 'copy hello world'"
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        text = args.strip()
        if not text:
            return CommandResult(success=False, response="What should I copy to the clipboard?")
        try:
            import pyperclip
            pyperclip.copy(text)
            logger.info(f"Copied to clipboard: '{text[:40]}'")
            return CommandResult(success=True, response=f"Copied to clipboard.")
        except ImportError:
            return CommandResult(
                success=False,
                response="pyperclip is not installed. Run: pip install pyperclip",
            )
        except Exception as exc:
            return CommandResult(success=False, response=f"Clipboard failed: {exc}")


class WhatTimeCommand(Command):
    name = "what time"
    aliases = [
        "what time is it", "current time", "tell me the time",
        "what's the time", "whats the time",
    ]
    description = "Tell the current time."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return CommandResult(success=True, response=f"It's {now}.")


class WhatDateCommand(Command):
    name = "what date"
    aliases = [
        "what's today", "whats today", "what day is it",
        "today's date", "current date",
    ]
    description = "Tell the current date."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return CommandResult(success=True, response=f"Today is {today}.")


# Register all system commands
_cmd_pkg.registry.register(VolumeCommand())
_cmd_pkg.registry.register(ScreenshotCommand())
_cmd_pkg.registry.register(ClipboardCommand())
_cmd_pkg.registry.register(WhatTimeCommand())
_cmd_pkg.registry.register(WhatDateCommand())
