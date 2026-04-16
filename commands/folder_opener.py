"""Folder opener command."""

import os

from loguru import logger

import commands as _cmd_pkg
from commands.base import Command, CommandResult
from config import load_apps


class OpenFolderCommand(Command):
    name = "open folder"
    aliases = ["open downloads", "open desktop", "open documents", "open pictures",
               "show folder", "browse"]
    description = "Open a folder in File Explorer. E.g. 'open downloads'"
    requires_confirmation = False

    def __init__(self):
        self._folders = load_apps().get("folders", [])

    def execute(self, args: str) -> CommandResult:
        target = args.lower().strip()

        # Check named folders from config
        for entry in self._folders:
            if target == entry.name.lower() or any(
                target == a.lower() for a in entry.aliases
            ):
                path = os.path.expandvars(entry.path)
                return self._open_path(path, entry.name)

        # Fallback: treat args as a literal path
        if args.strip():
            path = os.path.expandvars(args.strip())
            return self._open_path(path, path)

        return CommandResult(
            success=False,
            response="Which folder? Try 'open downloads' or 'open documents'.",
        )

    def _open_path(self, path: str, name: str) -> CommandResult:
        if not os.path.exists(path):
            return CommandResult(
                success=False,
                response=f"Folder not found: {path}",
            )
        try:
            os.startfile(path)
            logger.info(f"Opened folder: {name} → {path}")
            return CommandResult(success=True, response=f"Opening {name}.")
        except Exception as exc:
            logger.exception(f"Failed to open folder: {path}")
            return CommandResult(success=False, response=f"Could not open folder: {exc}")


_cmd_pkg.registry.register(OpenFolderCommand())
