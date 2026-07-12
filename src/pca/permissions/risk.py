"""Shell 命令风险分类。

修改前旧代码：
风险分类器占位模块，计划在第 3 周实现。

问题：权限系统没有稳定的分类 API，后续 policy/gate 无法复用同一份风险判断。
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


Command = str | Sequence[str]

SHELL_WRAPPER_EXECUTABLES = {
    "cmd",
    "cmd.exe",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
}


class RiskLevel(Enum):
    """命令执行前的粗粒度风险等级。"""

    SAFE = "safe"
    ASK = "ask"
    DENY = "deny"


@dataclass(frozen=True)
class RiskAssessment:
    """一次命令风险分类的结构化结果。"""

    level: RiskLevel
    reason: str
    matched_rule: str


def classify_command(command: Command) -> RiskAssessment:
    """对 shell 命令做最小风险分类，不负责执行拦截。"""
    parts = _normalize_command(command)
    command_text = " ".join(parts).strip()
    lowered_parts = tuple(part.lower() for part in parts)
    lowered_text = command_text.lower()

    deny_assessment = _match_deny_rules(lowered_parts, lowered_text)
    if deny_assessment is not None:
        return deny_assessment

    ask_assessment = _match_ask_rules(lowered_parts, lowered_text)
    if ask_assessment is not None:
        return ask_assessment

    return RiskAssessment(
        level=RiskLevel.SAFE,
        reason="Command appears read-only or locally bounded.",
        matched_rule="default_safe",
    )


def _normalize_command(command: Command) -> tuple[str, ...]:
    if isinstance(command, str):
        if command.strip() == "":
            raise ValueError("command must be a non-empty string or list of strings")
        try:
            parts = tuple(shlex.split(command, posix=False))
        except ValueError:
            parts = tuple(command.split())
        return parts or (command.strip(),)

    if isinstance(command, Sequence):
        if not command:
            raise ValueError("command must be a non-empty string or list of strings")
        if isinstance(command, (bytes, bytearray)):
            raise ValueError("command must be a non-empty string or list of strings")

        parts: list[str] = []
        for item in command:
            if not isinstance(item, str) or item.strip() == "":
                raise ValueError("command list items must be non-empty strings")
            parts.append(item.strip())
        return tuple(parts)

    raise ValueError("command must be a non-empty string or list of strings")


def _match_deny_rules(
    lowered_parts: tuple[str, ...],
    lowered_text: str,
) -> RiskAssessment | None:
    first = lowered_parts[0]

    if first in {"rm", "rmdir"} and any(part in {"-rf", "-fr", "-r"} for part in lowered_parts):
        return RiskAssessment(
            level=RiskLevel.DENY,
            reason="Recursive delete commands are destructive.",
            matched_rule="recursive_delete",
        )

    if first in {"del", "erase"} and any(part in {"/s", "/q"} for part in lowered_parts):
        return RiskAssessment(
            level=RiskLevel.DENY,
            reason="Windows recursive or quiet delete commands are destructive.",
            matched_rule="windows_delete",
        )

    if first == "remove-item" and (
        "-recurse" in lowered_parts or "-force" in lowered_parts
    ):
        return RiskAssessment(
            level=RiskLevel.DENY,
            reason="PowerShell Remove-Item with recurse or force is destructive.",
            matched_rule="powershell_remove_item",
        )

    if first == "format" or lowered_text.startswith("format "):
        return RiskAssessment(
            level=RiskLevel.DENY,
            reason="Disk format commands can destroy data.",
            matched_rule="format_disk",
        )

    return None


def _match_ask_rules(
    lowered_parts: tuple[str, ...],
    lowered_text: str,
) -> RiskAssessment | None:
    first = lowered_parts[0]

    # 修改前旧代码：
    # first = lowered_parts[0]
    # if first in {"curl", "wget", "invoke-webrequest", "iwr"}:
    #     ...
    #
    # 问题：cmd / PowerShell wrapper 会把真实子命令藏在后续 token 中，
    # 只检查 first 会让包装后的危险命令落入 default_safe。
    if _is_shell_wrapper(first):
        return RiskAssessment(
            level=RiskLevel.ASK,
            reason="Shell wrapper commands can hide nested command behavior.",
            matched_rule="shell_wrapper",
        )

    if first in {"curl", "wget", "invoke-webrequest", "iwr"}:
        return RiskAssessment(
            level=RiskLevel.ASK,
            reason="Network commands can read from or write to external systems.",
            matched_rule="network_access",
        )

    if _uses_inline_code(lowered_parts):
        return RiskAssessment(
            level=RiskLevel.ASK,
            reason="Inline code execution can run arbitrary logic.",
            matched_rule="inline_code",
        )

    if any(operator in lowered_text for operator in ("&&", "||", "|", ">", "<")):
        return RiskAssessment(
            level=RiskLevel.ASK,
            reason="Shell operators can chain commands or redirect data.",
            matched_rule="shell_operator",
        )

    return None


def _is_shell_wrapper(executable: str) -> bool:
    """识别可能隐藏内部命令语义的已知 shell wrapper。"""
    normalized = executable.strip().strip("\"'").replace("\\", "/")
    basename = normalized.rsplit("/", 1)[-1].lower()
    return basename in SHELL_WRAPPER_EXECUTABLES


def _uses_inline_code(lowered_parts: tuple[str, ...]) -> bool:
    executable = lowered_parts[0]
    if executable.endswith("python.exe"):
        executable = "python"
    if executable not in {"python", "python3", "py"}:
        return False
    return "-c" in lowered_parts


__all__ = ["RiskLevel", "RiskAssessment", "classify_command"]
