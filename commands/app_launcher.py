"""App launcher command — opens desktop applications by name."""

import os
import subprocess
from pathlib import Path

from loguru import logger

import commands as _cmd_pkg
from commands.base import Command, CommandResult
from config import load_apps


class OpenAppCommand(Command):
    name = "open"
    aliases = ["launch", "start", "run"]
    description = "Open an application or website. E.g. 'open chrome'"
    requires_confirmation = False

    def __init__(self):
        self._apps = load_apps()

    def execute(self, args: str) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                response="What would you like me to open?",
            )

        target = args.lower().strip()
        entry = self._find_entry(target)

        if entry is None:
            return CommandResult(
                success=False,
                response=f"I don't know how to open '{args}'. "
                         "You can add it to config/apps.yaml.",
            )

        if entry.is_web():
            import webbrowser
            webbrowser.open(entry.url)
            logger.info(f"Opened website: {entry.name} → {entry.url}")
            return CommandResult(success=True, response=f"Opening {entry.name}.")

        # Desktop app
        path = os.path.expandvars(entry.path)
        if not path:
            return CommandResult(success=False, response=f"No path configured for {entry.name}.")

        try:
            subprocess.Popen(
                [path],
                creationflags=subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            logger.info(f"Launched app: {entry.name} → {path}")
            return CommandResult(success=True, response=f"Opening {entry.name}.")
        except FileNotFoundError:
            logger.warning(f"App not found at path: {path}")
            return CommandResult(
                success=False,
                response=f"I couldn't find {entry.name} at {path}. "
                         "Please update the path in config/apps.yaml.",
            )
        except Exception as exc:
            logger.exception(f"Failed to launch {entry.name}")
            return CommandResult(success=False, response=f"Failed to open {entry.name}: {exc}")

    def _find_entry(self, target: str):
        """Find an app/website/folder matching the target string."""
        for section in ("apps", "websites", "folders"):
            for entry in self._apps.get(section, []):
                if target == entry.name.lower():
                    return entry
                if any(target == alias.lower() for alias in entry.aliases):
                    return entry
        return None


# Self-register on import
_cmd_pkg.registry.register(OpenAppCommand())
