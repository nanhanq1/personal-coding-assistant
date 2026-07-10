from pathlib import Path
from typing import Callable

import pytest

from pca.tools.base import ToolErrorCode
from pca.tools.file_tools import EditFileTool, WriteFileTool
from pca.tools.registry import ToolRegistry


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("write_file", {"content": "changed"}),
        ("edit_file", {"old_text": "original", "new_text": "changed"}),
    ],
)
def test_file_tools_reject_outside_workspace_without_side_effect(
    tmp_path: Path,
    tool_name: str,
    arguments: dict[str, str],
) -> None:
    """工作区外的 write/edit 必须在 permission gate 前停止。"""
    outside = tmp_path.parent / "safety-outside-sentinel.txt"
    outside.write_text("original", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(WriteFileTool())
    registry.register(EditFileTool())

    result = registry.run(
        tool_name,
        {
            **arguments,
            "path": str(outside),
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_code is ToolErrorCode.INVALID_ARGUMENT
    assert outside.read_text(encoding="utf-8") == "original"


def test_overwrite_requires_approval_and_preserves_file(
    tmp_path: Path,
    audit_path: Path,
    read_one_audit_event: Callable[[Path], dict[str, object]],
) -> None:
    """覆盖已有文件需要 approval，且不能先写入新内容。"""
    target = tmp_path / "existing.txt"
    target.write_text("original", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(WriteFileTool(audit_path=audit_path))

    result = registry.run(
        "write_file",
        {
            "path": "existing.txt",
            "content": "changed",
            "workspace_root": str(tmp_path),
        },
    )

    event = read_one_audit_event(audit_path)
    assert result.ok is False
    assert result.error_code is ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert target.read_text(encoding="utf-8") == "original"
    assert event["action"] == "ask"
    assert event["matched_rule"] == "overwrite_existing_file"
    assert event["executed"] is False


def test_delete_like_edit_requires_approval_and_preserves_file(
    tmp_path: Path,
    audit_path: Path,
    read_one_audit_event: Callable[[Path], dict[str, object]],
) -> None:
    """删除式 edit 必须需要 approval，且不能删除原有文本。"""
    target = tmp_path / "module.py"
    target.write_text("important code\n", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(EditFileTool(audit_path=audit_path))

    result = registry.run(
        "edit_file",
        {
            "path": "module.py",
            "old_text": "important code\n",
            "new_text": "",
            "workspace_root": str(tmp_path),
        },
    )

    event = read_one_audit_event(audit_path)
    assert result.ok is False
    assert result.error_code is ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert target.read_text(encoding="utf-8") == "important code\n"
    assert event["action"] == "ask"
    assert event["matched_rule"] == "delete_like_edit"
    assert event["executed"] is False
