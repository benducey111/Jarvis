"""Typing automation command — types text into the active window."""

import time

from loguru import logger

import commands as _cmd_pkg
from commands.base import Command, CommandResult


class TypeTextCommand(Command):
    name = "type"
    aliases = ["type out", "write", "input"]
    description = "Type text into the currently active window. E.g. 'type hello world'"
    requires_confirmation = True
    confirmation_message = "Are you sure you want to type into the active window?"

    def execute(self, args: str) -> CommandResult:
        text = args.strip()
        if not text:
            return CommandResult(success=False, response="What text should I type?")

        try:
            import pyautogui

            # Brief delay so Jarvis window loses focus first
            time.sleep(0.4)
            pyautogui.typewrite(text, interval=0.04)
            logger.info(f"Typed text: '{text[:40]}{'...' if len(text) > 40 else ''}'")
            return CommandResult(success=True, response=f"Typed: {text[:60]}")
        except ImportError:
            return CommandResult(
                success=False,
                response="pyautogui is not installed. Run: pip install pyautogui",
            )
        except Exception as exc:
            logger.exception("TypeTextCommand failed")
            return CommandResult(success=False, response=f"Typing failed: {exc}")


_cmd_pkg.registry.register(TypeTextCommand())
