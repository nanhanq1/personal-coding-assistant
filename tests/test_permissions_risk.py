import sys

import pytest

from pca.permissions.risk import RiskLevel, classify_command


def test_classifies_read_only_commands_as_safe() -> None:
    """只读或本地验证命令默认是 SAFE。"""
    safe_commands = [
        "git status",
        "pytest -q",
        "python -m compileall src examples -q",
        ["git", "diff"],
    ]

    for command in safe_commands:
        assessment = classify_command(command)

        assert assessment.level is RiskLevel.SAFE
        assert assessment.reason
        assert assessment.matched_rule


def test_classifies_network_and_inline_code_commands_as_ask() -> None:
    """联网和内联代码执行命令需要用户确认。"""
    ask_commands = [
        "curl https://example.com",
        "Invoke-WebRequest https://example.com",
        [sys.executable, "-c", "print('hello')"],
        "python -c \"print('hello')\"",
    ]

    for command in ask_commands:
        assessment = classify_command(command)

        assert assessment.level is RiskLevel.ASK
        assert assessment.reason
        assert assessment.matched_rule


@pytest.mark.parametrize(
    "command",
    [
        "cmd /c del /s /q harmless-target",
        "powershell -Command Remove-Item harmless-target -Recurse -Force",
        "pwsh -Command Get-ChildItem",
        ["cmd.exe", "/c", "echo", "hello"],
        ["PoWeRsHeLl.ExE", "-Command", "Get-ChildItem"],
        [r"C:\Windows\System32\cmd.exe", "/c", "echo", "hello"],
        [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-Command",
            "Get-ChildItem",
        ],
        r'"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -Command Get-ChildItem',
    ],
)
def test_classifies_shell_wrappers_as_ask(command) -> None:
    """shell wrapper 可以隐藏内部行为，默认必须 ASK。"""
    assessment = classify_command(command)

    assert assessment.level is RiskLevel.ASK
    assert assessment.matched_rule == "shell_wrapper"
    assert assessment.reason


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf /",
        "del /s /q *",
        "Remove-Item -Recurse -Force .",
        "format C:",
    ],
)
def test_classifies_destructive_commands_as_deny(command: str) -> None:
    """明显破坏性命令直接 DENY。"""
    assessment = classify_command(command)

    assert assessment.level is RiskLevel.DENY
    assert assessment.reason
    assert assessment.matched_rule


def test_rejects_empty_command() -> None:
    """空命令不是可分类命令，应在权限边界直接报错。"""
    with pytest.raises(ValueError, match="command"):
        classify_command("")

    with pytest.raises(ValueError, match="command"):
        classify_command([])
