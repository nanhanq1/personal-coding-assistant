"""文件变更风险分类。

修改前旧代码：
文件工具只做 workspace_root 路径边界和基础参数校验，write_file / edit_file
在路径合法时会直接写盘。

问题：覆盖已有文件和删除式编辑虽然位于工作区内，但仍可能破坏用户代码，
需要进入 permission policy，而不是静默执行。
"""

from __future__ import annotations

from pathlib import Path

from pca.permissions.risk import RiskAssessment, RiskLevel


LARGE_EDIT_OLD_TEXT_MIN_CHARS = 80
LARGE_EDIT_REDUCTION_RATIO = 0.5


def classify_file_change(
    *,
    tool_name: str,
    path: Path,
    old_text: str | None = None,
    new_text: str | None = None,
) -> RiskAssessment:
    """对文件写入或编辑做执行前风险分类，不负责路径边界校验。"""
    if not isinstance(tool_name, str) or tool_name.strip() == "":
        raise ValueError("tool_name must be a non-empty string")
    if not isinstance(path, Path):
        raise TypeError("path must be a Path")

    if tool_name == "write_file":
        if path.exists():
            return RiskAssessment(
                level=RiskLevel.ASK,
                reason="Writing to an existing file can overwrite user work.",
                matched_rule="overwrite_existing_file",
            )
        return RiskAssessment(
            level=RiskLevel.SAFE,
            reason="Writing a new file inside the workspace is allowed by default.",
            matched_rule="new_file_write",
        )

    if tool_name == "edit_file":
        _validate_edit_text(old_text=old_text, new_text=new_text)
        if new_text == "" or _is_large_reduction(old_text=old_text, new_text=new_text):
            return RiskAssessment(
                level=RiskLevel.ASK,
                reason="Delete-like edits can remove meaningful user code.",
                matched_rule="delete_like_edit",
            )
        return RiskAssessment(
            level=RiskLevel.SAFE,
            reason="Small exact text replacements are allowed by default.",
            matched_rule="small_exact_edit",
        )

    raise ValueError(f"unsupported file tool: {tool_name}")


def _validate_edit_text(*, old_text: str | None, new_text: str | None) -> None:
    if not isinstance(old_text, str) or old_text == "":
        raise ValueError("old_text must be a non-empty string")
    if not isinstance(new_text, str):
        raise ValueError("new_text must be a string")


def _is_large_reduction(*, old_text: str, new_text: str) -> bool:
    """识别大段删除式替换，避免把整块代码清掉但仍伪装成普通 edit。"""
    if len(old_text) < LARGE_EDIT_OLD_TEXT_MIN_CHARS:
        return False
    return len(new_text) < len(old_text) * LARGE_EDIT_REDUCTION_RATIO


__all__ = ["classify_file_change"]

