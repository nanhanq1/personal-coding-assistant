import pytest

from pca.permissions.file_risk import classify_file_change
from pca.permissions.risk import RiskLevel
from pca.tools import create_coding_tool_registry


def test_classifies_new_write_file_as_safe(tmp_path):
    """新建文件默认是低风险文件变更。"""
    assessment = classify_file_change(
        tool_name="write_file",
        path=tmp_path / "new.txt",
    )

    assert assessment.level is RiskLevel.SAFE
    assert assessment.matched_rule == "new_file_write"


def test_classifies_overwrite_existing_file_as_ask(tmp_path):
    """覆盖已有文件需要人工确认，不能和新建文件同等处理。"""
    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("old content", encoding="utf-8")

    assessment = classify_file_change(
        tool_name="write_file",
        path=existing_file,
    )

    assert assessment.level is RiskLevel.ASK
    assert assessment.matched_rule == "overwrite_existing_file"


def test_classifies_delete_like_edit_as_ask(tmp_path):
    """把目标文本替换为空字符串属于删除式编辑，需要人工确认。"""
    assessment = classify_file_change(
        tool_name="edit_file",
        path=tmp_path / "module.py",
        old_text="print('hello')\n",
        new_text="",
    )

    assert assessment.level is RiskLevel.ASK
    assert assessment.matched_rule == "delete_like_edit"


def test_file_gate_does_not_overwrite_existing_file_without_approval(tmp_path):
    """通过 registry 调用覆盖写入时，ASK 必须在写盘前拦截。"""
    registry = create_coding_tool_registry()
    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("old content", encoding="utf-8")

    result = registry.run(
        "write_file",
        {
            "path": "existing.txt",
            "content": "new content",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_type == "PermissionError"
    assert "approval required" in result.error_message.lower()
    assert "overwrite_existing_file" in result.error_message
    assert existing_file.read_text(encoding="utf-8") == "old content"


def test_file_gate_does_not_apply_delete_like_edit_without_approval(tmp_path):
    """删除式 edit_file 必须在写盘前拦截，保留原文件内容。"""
    registry = create_coding_tool_registry()
    test_file = tmp_path / "module.py"
    original = "print('hello')\nprint('done')\n"
    test_file.write_text(original, encoding="utf-8")

    result = registry.run(
        "edit_file",
        {
            "path": "module.py",
            "old_text": "print('hello')\n",
            "new_text": "",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_type == "PermissionError"
    assert "approval required" in result.error_message.lower()
    assert "delete_like_edit" in result.error_message
    assert test_file.read_text(encoding="utf-8") == original

