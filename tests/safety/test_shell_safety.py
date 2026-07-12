import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable

import pytest

from pca.tools.base import ToolErrorCode
from pca.tools.registry import ToolRegistry
from pca.tools.shell_tools import ShellCommandTool

@pytest.mark.parametrize(
    ("command", "expected_code", "expected_rule", "expected_action"),
    [
        (
            "rm -rf .",
            ToolErrorCode.PERMISSION_DENIED,
            "recursive_delete",
            "deny",
        ),
        (
            "curl https://example.com",
            ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
            "network_access",
            "ask",
        ),
        (
            [sys.executable, "-c", "print('blocked')"],
            ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
            "inline_code",
            "ask",
        ),
        (
            "cmd /c del /s /q harmless-target",
            ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
            "shell_wrapper",
            "ask",
        ),
        (
            ["powershell.exe", "-Command", "Remove-Item", "harmless-target"],
            ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
            "shell_wrapper",
            "ask",
        ),
    ],
)
def test_shell_safety_gate_blocks_before_runtime(
    tmp_path: Path,
    audit_path: Path,
    recording_runtime: Any,
    read_one_audit_event: Callable[[Path], dict[str, object]],
    command: str | list[str],
    expected_code: ToolErrorCode,
    expected_rule: str,
    expected_action: str,
) -> None:
    """危险、网络和 inline code 都必须在 runtime 前停止。"""
    registry = ToolRegistry()
    registry.register(
        ShellCommandTool(runtime=recording_runtime, audit_path=audit_path),
    )

    result = registry.run(
        "run_command",
        {
            "command": command,
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    event = read_one_audit_event(audit_path)
    assert result.ok is False
    assert result.error_code is expected_code
    assert expected_rule in result.error_message
    assert recording_runtime.calls == []
    assert event["action"] == expected_action
    assert event["matched_rule"] == expected_rule
    assert event["executed"] is False


def test_shell_audit_does_not_include_sensitive_env_value(
    tmp_path: Path,
    audit_path: Path,
    recording_runtime: Any,
    read_one_audit_event: Callable[[Path], dict[str, object]],
) -> None:
    """安全命令的 audit 只能保留摘要，不能记录环境变量 secret。"""
    secret = "safety-" + uuid.uuid4().hex
    registry = ToolRegistry()
    registry.register(
        ShellCommandTool(runtime=recording_runtime, audit_path=audit_path),
    )

    result = registry.run(
        "run_command",
        {
            "command": "echo safe",
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
            "env": {"PCA_TEST_API_TOKEN": secret},
        },
    )

    payload = json.dumps(read_one_audit_event(audit_path))
    assert result.ok is True
    assert recording_runtime.calls != []
    if secret in payload:
        raise AssertionError("permission audit contained a sensitive value")
