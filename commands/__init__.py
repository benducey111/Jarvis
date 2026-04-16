"""Command registry and auto-import of all command modules.

Usage:
    from commands import registry

    # Dispatch user input
    command, args = registry.dispatch("open chrome")
    if command:
        result = command.execute(args)

    # List all registered commands
    registry.list_commands()
"""

from loguru import logger
from utils.singleton import SingletonMeta


class CommandRegistry(metaclass=SingletonMeta):
    """Singleton registry that maps trigger phrases → Command instances."""

    def __init__(self):
        self._commands: dict[str, object] = {}   # trigger → Command

    def register(self, command) -> None:
        """Register a command and all its aliases.

        Args:
            command: A Command subclass instance.
        """
        triggers = [command.name] + list(command.aliases)
        for trigger in triggers:
            key = trigger.lower().strip()
            if key in self._commands:
                logger.warning(
                    f"CommandRegistry: trigger '{key}' already registered "
                    f"by {self._commands[key].name!r}, overwriting with {command.name!r}"
                )
            self._commands[key] = command
        logger.debug(f"Registered command: {command.name!r} with triggers {triggers}")

    def dispatch(self, text: str) -> tuple:
        """Find a matching command for the input text.

        Tries to match from longest trigger phrase to shortest for specificity.

        Args:
            text: Normalised (lowercased, stripped) user input.

        Returns:
            (Command, args_string) or (None, text) if no match.
        """
        normalized = text.lower().strip()

        # Sort triggers by length descending so "search google for" beats "search"
        for trigger in sorted(self._commands.keys(), key=len, reverse=True):
            if normalized.startswith(trigger):
                args = normalized[len(trigger):].strip()
                return self._commands[trigger], args

        return None, text

    def list_commands(self) -> list:
        """Return a deduplicated list of registered Command instances."""
        seen = set()
        result = []
        for cmd in self._commands.values():
            if id(cmd) not in seen:
                seen.add(id(cmd))
                result.append(cmd)
        return result


# Module-level singleton instance
registry = CommandRegistry()


# ---------------------------------------------------------------------------
# Auto-import all command modules so they self-register on import of this package
# ---------------------------------------------------------------------------

def _load_commands() -> None:
    """Import every command module.  Each module registers itself on import."""
    modules = [
        "commands.app_launcher",
        "commands.web_search",
        "commands.typer",
        "commands.folder_opener",
        "commands.system_control",
        "commands.jarvis_control",
    ]
    for module in modules:
        try:
            __import__(module)
            logger.debug(f"Loaded command module: {module}")
        except ImportError as exc:
            logger.warning(f"Could not load command module {module}: {exc}")

    # Load any user plugins from the plugins/ directory
    _load_plugins()


def _load_plugins() -> None:
    """Scan the plugins/ directory and import any Command subclasses found."""
    import importlib
    import pkgutil
    import plugins as _plugins_pkg

    for finder, name, _ in pkgutil.iter_modules(_plugins_pkg.__path__):
        full_name = f"plugins.{name}"
        try:
            importlib.import_module(full_name)
            logger.info(f"Loaded plugin: {full_name}")
        except Exception as exc:
            logger.warning(f"Failed to load plugin {full_name}: {exc}")


_load_commands()
