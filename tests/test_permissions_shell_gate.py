import json
from typing import Any

import pytest

from pca.tools import shell_tools
from pca.tools import base as tool_base
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


def _read_one_audit_event(audit_path) -> dict[str, Any]:
    """读取本测试写入的唯一审计记录。"""
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


def test_shell_gate_denies_destructive_command_before_runtime(tmp_path) -> None:
    """DENY 命令必须在 shell runtime 前被拦截。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=tmp_path / "audit.jsonl"))

    result = registry.run(
        "run_command",
        {
            "command": "rm -rf .",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    assert result.ok is False
    assert result.error_type == "PermissionError"
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_DENIED
    assert "deny" in result.error_message.lower()
    assert "recursive_delete" in result.error_message
    assert runtime.calls == []


def test_shell_gate_requires_approval_for_ask_command_before_runtime(tmp_path) -> None:
    """ASK 命令不能静默执行，必须先返回待审批失败。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=tmp_path / "audit.jsonl"))

    result = registry.run(
        "run_command",
        {
            "command": "curl https://example.com",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    assert result.ok is False
    assert result.error_type == "PermissionError"
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert "ask" in result.error_message.lower()
    assert "approval required" in result.error_message.lower()
    assert "network_access" in result.error_message
    assert runtime.calls == []


@pytest.mark.parametrize(
    "command",
    [
        "cmd /c del /s /q harmless-target",
        ["powershell.exe", "-Command", "Get-ChildItem"],
    ],
)
def test_shell_gate_requires_approval_for_shell_wrapper_before_runtime(
    tmp_path,
    command,
) -> None:
    """包装命令必须在 runtime 前转成待审批失败并留下摘要审计。"""
    runtime = RecordingRuntime()
    audit_path = tmp_path / "audit.jsonl"
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=audit_path))

    result = registry.run(
        "run_command",
        {
            "command": command,
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.ok is False
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert "shell_wrapper" in result.error_message
    assert runtime.calls == []
    assert event["action"] == "ask"
    assert event["matched_rule"] == "shell_wrapper"
    assert event["executed"] is False


def test_shell_gate_allows_safe_command_through_original_runtime_path(tmp_path) -> None:
    """ALLOW 命令保持原来的 runtime.run(arguments) 执行路径。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=tmp_path / "audit.jsonl"))
    arguments = {
        "command": "echo hello",
        "workspace_root": str(tmp_path),
        "timeout_seconds": 5,
    }

    result = registry.run("run_command", arguments)

    assert result.ok is True
    assert result.result["stdout"] == "allowed\n"
    assert runtime.calls == [arguments]


def test_shell_gate_records_allow_before_entering_runtime(tmp_path) -> None:
    """ALLOW 需要先落一条摘要审计，再进入真实 runtime。"""
    runtime = RecordingRuntime()
    audit_path = tmp_path / "permission_audit.jsonl"
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=audit_path))
    arguments = {
        "command": "echo api_token=top-secret",
        "workspace_root": str(tmp_path),
        "timeout_seconds": 5,
    }

    result = registry.run("run_command", arguments)

    event = _read_one_audit_event(audit_path)
    assert result.ok is True
    assert runtime.calls == [arguments]
    assert event["tool_name"] == "run_command"
    assert event["action"] == "allow"
    assert event["risk_level"] == "safe"
    assert event["matched_rule"] == "default_safe"
    assert event["executed"] is True
    assert "top-secret" not in json.dumps(event)


def test_shell_gate_records_ask_without_entering_runtime(tmp_path) -> None:
    """ASK 即使不执行，也需要留下 executed=false 的审计事实。"""
    runtime = RecordingRuntime()
    audit_path = tmp_path / "permission_audit.jsonl"
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=audit_path))

    result = registry.run(
        "run_command",
        {
            "command": "curl https://example.com",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert runtime.calls == []
    assert event["action"] == "ask"
    assert event["matched_rule"] == "network_access"
    assert event["executed"] is False


def test_shell_gate_records_deny_without_entering_runtime(tmp_path) -> None:
    """DENY 即使不执行，也需要留下 executed=false 的审计事实。"""
    runtime = RecordingRuntime()
    audit_path = tmp_path / "permission_audit.jsonl"
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=audit_path))

    result = registry.run(
        "run_command",
        {
            "command": "rm -rf .",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_DENIED
    assert runtime.calls == []
    assert event["action"] == "deny"
    assert event["matched_rule"] == "recursive_delete"
    assert event["executed"] is False


def test_shell_allow_fails_closed_when_audit_write_fails(tmp_path, monkeypatch) -> None:
    """ALLOW 的审计写入失败时，真实 runtime 绝不能被调用。"""
    runtime = RecordingRuntime()
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=tmp_path / "audit.jsonl"))

    def raise_audit_error(*args, **kwargs) -> None:
        raise OSError("audit storage is unavailable")

    monkeypatch.setattr(shell_tools, "record_permission_decision", raise_audit_error)
    result = registry.run(
        "run_command",
        {
            "command": "echo hello",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    assert result.ok is False
    assert result.error_code is tool_base.ToolErrorCode.RUNTIME_FAILED
    assert runtime.calls == []
