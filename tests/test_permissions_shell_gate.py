from typing import Any

from pca.tools.registry import ToolRegistry
from pca.tools.shell_tools import ShellCommandTool


class RecordingRuntime:
    """记录 shell gate 是否真的放行到执行层。"""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(arguments)
        return {
            "stdout": "allowed\n",
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
        }


def test_shell_gate_denies_destructive_command_before_runtime() -> None:
    """DENY 命令必须在 shell runtime 前被拦截。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime))

    result = registry.run(
        "run_command",
        {
            "command": "rm -rf .",
            "workspace_root": ".",
            "timeout_seconds": 5,
        },
    )

    assert result.ok is False
    assert result.error_type == "PermissionError"
    assert "deny" in result.error_message.lower()
    assert "recursive_delete" in result.error_message
    assert runtime.calls == []


def test_shell_gate_requires_approval_for_ask_command_before_runtime() -> None:
    """ASK 命令不能静默执行，必须先返回待审批失败。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime))

    result = registry.run(
        "run_command",
        {
            "command": "curl https://example.com",
            "workspace_root": ".",
            "timeout_seconds": 5,
        },
    )

    assert result.ok is False
    assert result.error_type == "PermissionError"
    assert "ask" in result.error_message.lower()
    assert "approval required" in result.error_message.lower()
    assert "network_access" in result.error_message
    assert runtime.calls == []


def test_shell_gate_allows_safe_command_through_original_runtime_path() -> None:
    """ALLOW 命令保持原来的 runtime.run(arguments) 执行路径。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime))
    arguments = {
        "command": "echo hello",
        "workspace_root": ".",
        "timeout_seconds": 5,
    }

    result = registry.run("run_command", arguments)

    assert result.ok is True
    assert result.result["stdout"] == "allowed\n"
    assert runtime.calls == [arguments]
