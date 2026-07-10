import json

import pytest

from pca.permissions.policy import DecisionAction, PermissionDecision
from pca.permissions.file_risk import classify_file_change
from pca.permissions.risk import RiskLevel
from pca.tools import create_coding_tool_registry
from pca.tools import base as tool_base
from pca.tools import file_tools
from pca.tools.file_tools import WriteFileTool
from pca.tools.registry import ToolRegistry


def _read_one_audit_event(audit_path) -> dict[str, object]:
    """读取本测试写入的唯一审计记录。"""
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


class DenyPolicy:
    """只供测试覆盖 file gate 的 deny 分支，不改变生产风险分类。"""

    def decide(self, assessment):
        return PermissionDecision(
            action=DecisionAction.DENY,
            reason="Test policy denies every file change.",
            assessment=assessment,
        )


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
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
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
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert "approval required" in result.error_message.lower()
    assert "delete_like_edit" in result.error_message
    assert test_file.read_text(encoding="utf-8") == original


def test_file_gate_records_allow_before_writing_new_file(tmp_path) -> None:
    """新建文件允许写入前必须有摘要审计记录。"""
    audit_path = tmp_path / "permission_audit.jsonl"
    registry = ToolRegistry()
    registry.register(WriteFileTool(audit_path=audit_path))

    result = registry.run(
        "write_file",
        {
            "path": "new.txt",
            "content": "api_token=top-secret",
            "workspace_root": str(tmp_path),
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.ok is True
    assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "api_token=top-secret"
    assert event["tool_name"] == "write_file"
    assert event["action"] == "allow"
    assert event["matched_rule"] == "new_file_write"
    assert event["executed"] is True
    assert "top-secret" not in json.dumps(event)


def test_file_gate_records_ask_without_overwriting_file(tmp_path) -> None:
    """覆盖已有文件的 ASK 必须审计且保留原文件。"""
    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("old content", encoding="utf-8")
    audit_path = tmp_path / "permission_audit.jsonl"
    registry = ToolRegistry()
    registry.register(WriteFileTool(audit_path=audit_path))

    result = registry.run(
        "write_file",
        {
            "path": "existing.txt",
            "content": "new content",
            "workspace_root": str(tmp_path),
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert existing_file.read_text(encoding="utf-8") == "old content"
    assert event["action"] == "ask"
    assert event["matched_rule"] == "overwrite_existing_file"
    assert event["executed"] is False


def test_file_gate_records_injected_deny_without_writing_file(tmp_path) -> None:
    """注入 DENY 策略时，file gate 也必须审计且不得写盘。"""
    audit_path = tmp_path / "permission_audit.jsonl"
    registry = ToolRegistry()
    registry.register(WriteFileTool(permission_policy=DenyPolicy(), audit_path=audit_path))

    result = registry.run(
        "write_file",
        {
            "path": "blocked.txt",
            "content": "blocked",
            "workspace_root": str(tmp_path),
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_DENIED
    assert not (tmp_path / "blocked.txt").exists()
    assert event["action"] == "deny"
    assert event["executed"] is False


def test_file_allow_fails_closed_when_audit_write_fails(tmp_path, monkeypatch) -> None:
    """ALLOW 的审计存储不可用时，不得创建目标文件。"""
    registry = ToolRegistry()
    registry.register(WriteFileTool(audit_path=tmp_path / "permission_audit.jsonl"))

    def raise_audit_error(*args, **kwargs) -> None:
        raise OSError("audit storage is unavailable")

    monkeypatch.setattr(file_tools, "record_permission_decision", raise_audit_error)
    result = registry.run(
        "write_file",
        {
            "path": "not-written.txt",
            "content": "content",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_code is tool_base.ToolErrorCode.RUNTIME_FAILED
    assert not (tmp_path / "not-written.txt").exists()
