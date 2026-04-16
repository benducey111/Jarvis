"""Web search command."""

import webbrowser
from urllib.parse import quote_plus

from loguru import logger

import commands as _cmd_pkg
from commands.base import Command, CommandResult


class SearchWebCommand(Command):
    name = "search"
    aliases = [
        "search for",
        "search google for",
        "google",
        "look up",
        "find",
        "search the web for",
    ]
    description = "Search Google. E.g. 'search for Python tutorials'"
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        query = args.strip()
        if not query:
            return CommandResult(success=False, response="What would you like me to search for?")

        url = f"https://www.google.com/search?q={quote_plus(query)}"
        webbrowser.open(url)
        logger.info(f"Web search: '{query}' → {url}")
        return CommandResult(success=True, response=f"Searching Google for '{query}'.")


_cmd_pkg.registry.register(SearchWebCommand())
