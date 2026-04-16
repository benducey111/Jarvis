"""Built-in Jarvis control commands."""

import commands as _cmd_pkg
from commands.base import Command, CommandResult


class StopCommand(Command):
    name = "stop"
    aliases = ["stop talking", "be quiet", "shut up", "silence"]
    description = "Stop Jarvis from speaking."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        # The AssistantEngine handles TTS stopping when it sees this result
        return CommandResult(
            success=True,
            response="",
            speak=False,
            data={"action": "stop_speaking"},
        )


class ClearHistoryCommand(Command):
    name = "clear history"
    aliases = [
        "clear chat", "reset conversation", "forget everything",
        "start over", "clear conversation",
    ]
    description = "Clear the conversation history."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        return CommandResult(
            success=True,
            response="Conversation cleared.",
            data={"action": "clear_history"},
        )


class SafeModeOnCommand(Command):
    name = "enable safe mode"
    aliases = ["turn on safe mode", "safe mode on", "activate safe mode"]
    description = "Enable safe mode (require confirmation for risky actions)."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        return CommandResult(
            success=True,
            response="Safe mode enabled. I'll ask for confirmation before risky actions.",
            data={"action": "set_safe_mode", "value": True},
        )


class SafeModeOffCommand(Command):
    name = "disable safe mode"
    aliases = ["turn off safe mode", "safe mode off", "deactivate safe mode"]
    description = "Disable safe mode."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        return CommandResult(
            success=True,
            response="Safe mode disabled. I'll execute commands without confirmation.",
            data={"action": "set_safe_mode", "value": False},
        )


class HelpCommand(Command):
    name = "help"
    aliases = ["what can you do", "show commands", "list commands", "commands"]
    description = "List available commands."
    requires_confirmation = False

    def execute(self, args: str) -> CommandResult:
        from commands import registry
        cmds = registry.list_commands()
        lines = [f"• {c.name}: {c.description}" for c in cmds if c.description]
        text = "Here's what I can do:\n" + "\n".join(lines[:15])
        if len(cmds) > 15:
            text += f"\n…and {len(cmds) - 15} more."
        return CommandResult(success=True, response=text, speak=False)


_cmd_pkg.registry.register(StopCommand())
_cmd_pkg.registry.register(ClearHistoryCommand())
_cmd_pkg.registry.register(SafeModeOnCommand())
_cmd_pkg.registry.register(SafeModeOffCommand())
_cmd_pkg.registry.register(HelpCommand())
