from importlib import import_module
from typing import Any

from pca.runtime.shell_runtime import ShellRuntime
from pca.tools.registry import ToolRegistry
from pca.tools.shell_tools import ShellCommandTool


def _command_runtime_type() -> type:
    module = import_module("pca.runtime.interface")
    return module.CommandRuntime


class FakeCommandRuntime:
    """测试用命令执行器，只实现 CommandRuntime 要求的最小 run(...) 接口。"""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(arguments)
        return {
            "stdout": "fake runtime\n",
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
        }


def test_shell_runtime_satisfies_command_runtime_protocol() -> None:
    """当前本地 shell runtime 应该满足命令执行接口。"""
    CommandRuntime = _command_runtime_type()

    assert isinstance(ShellRuntime(), CommandRuntime)


def test_fake_runtime_satisfies_command_runtime_protocol() -> None:
    """fake runtime 只要实现 run(arguments) 就能作为命令执行器。"""
    CommandRuntime = _command_runtime_type()
    runtime = FakeCommandRuntime()

    assert isinstance(runtime, CommandRuntime)


def test_shell_command_tool_depends_on_command_runtime_interface() -> None:
    """ShellCommandTool 应依赖 CommandRuntime，而不是具体 ShellRuntime。"""
    runtime = FakeCommandRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime))
    arguments = {
        "command": "echo hello",
        "workspace_root": ".",
        "timeout_seconds": 5,
    }

    result = registry.run("run_command", arguments)

    assert result.ok is True
    assert result.result["stdout"] == "fake runtime\n"
    assert runtime.calls == [arguments]
