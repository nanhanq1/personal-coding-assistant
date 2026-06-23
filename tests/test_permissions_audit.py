import json
from datetime import datetime, timezone

from pca.permissions.audit import PermissionAuditEvent, append_audit_event
from pca.permissions.policy import DecisionAction


def test_audit_event_keeps_permission_fact_fields() -> None:
    """审计事件应记录权限判断事实，不负责改变执行结果。"""
    happened_at = datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc)

    event = PermissionAuditEvent(
        timestamp=happened_at,
        tool_name="run_command",
        action=DecisionAction.ASK,
        risk_level="ask",
        matched_rule="network_access",
        reason="Network command requires approval.",
        executed=False,
    )

    assert event.timestamp == happened_at
    assert event.tool_name == "run_command"
    assert event.action is DecisionAction.ASK
    assert event.risk_level == "ask"
    assert event.matched_rule == "network_access"
    assert event.executed is False


def test_audit_event_serializes_to_stable_dict() -> None:
    """审计事件应能转成稳定 JSON 字段，枚举和值对象不能泄漏进去。"""
    event = PermissionAuditEvent(
        timestamp=datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc),
        tool_name="write_file",
        action=DecisionAction.ALLOW,
        risk_level="safe",
        matched_rule="new_file_write",
        reason="New file write is allowed.",
        executed=True,
    )

    assert event.to_dict() == {
        "timestamp": "2026-06-22T10:00:00+00:00",
        "tool_name": "write_file",
        "action": "allow",
        "risk_level": "safe",
        "matched_rule": "new_file_write",
        "reason": "New file write is allowed.",
        "executed": True,
    }


def test_append_audit_event_writes_one_json_object_per_line(tmp_path) -> None:
    """JSONL 审计文件应一行一个事件，便于后续追加和回放。"""
    audit_path = tmp_path / "permission_audit.jsonl"
    event = PermissionAuditEvent(
        timestamp=datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc),
        tool_name="edit_file",
        action=DecisionAction.DENY,
        risk_level="deny",
        matched_rule="delete_like_edit",
        reason="Delete-like edit was blocked.",
        executed=False,
    )

    append_audit_event(audit_path, event)

    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == event.to_dict()
