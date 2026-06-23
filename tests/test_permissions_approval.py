from datetime import datetime, timedelta, timezone

import pytest

from pca.permissions.approval import ApprovalDecision, ApprovalRequest
from pca.permissions.policy import DecisionAction, PermissionDecision
from pca.permissions.risk import RiskAssessment, RiskLevel


def _ask_decision() -> PermissionDecision:
    assessment = RiskAssessment(
        level=RiskLevel.ASK,
        reason="Network commands can read from or write to external systems.",
        matched_rule="network_access",
    )
    return PermissionDecision(
        action=DecisionAction.ASK,
        reason="Ask risk assessments require approval before execution.",
        assessment=assessment,
    )


def test_approval_request_keeps_policy_context_and_expiration() -> None:
    """审批请求应保留策略判断上下文，并能判断是否过期。"""
    created_at = datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc)
    expires_at = created_at + timedelta(minutes=5)

    request = ApprovalRequest(
        request_id="req-1",
        tool_name="run_command",
        command_summary="curl https://example.com",
        decision=_ask_decision(),
        created_at=created_at,
        expires_at=expires_at,
    )

    assert request.request_id == "req-1"
    assert request.tool_name == "run_command"
    assert request.command_summary == "curl https://example.com"
    assert request.decision.action is DecisionAction.ASK
    assert not request.is_expired(created_at + timedelta(minutes=4))
    assert request.is_expired(expires_at)


def test_approval_decision_approve_records_user_confirmation() -> None:
    """批准决策应记录 request id、用户理由和决策时间。"""
    decided_at = datetime(2026, 6, 22, 9, 3, tzinfo=timezone.utc)

    decision = ApprovalDecision.approve(
        request_id="req-1",
        user_reason="Only downloads public docs.",
        decided_at=decided_at,
    )

    assert decision.request_id == "req-1"
    assert decision.approved is True
    assert decision.user_reason == "Only downloads public docs."
    assert decision.decided_at == decided_at


def test_approval_decision_reject_records_user_reason() -> None:
    """拒绝决策应记录 request id、用户理由和决策时间。"""
    decided_at = datetime(2026, 6, 22, 9, 4, tzinfo=timezone.utc)

    decision = ApprovalDecision.reject(
        request_id="req-1",
        user_reason="Network access is not needed for this task.",
        decided_at=decided_at,
    )

    assert decision.request_id == "req-1"
    assert decision.approved is False
    assert decision.user_reason == "Network access is not needed for this task."
    assert decision.decided_at == decided_at


def test_approval_request_rejects_invalid_inputs() -> None:
    """审批请求边界应拒绝空身份、空工具名和无效过期时间。"""
    created_at = datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc)
    expires_at = created_at + timedelta(minutes=5)

    with pytest.raises(ValueError, match="request_id"):
        ApprovalRequest(
            request_id="",
            tool_name="run_command",
            command_summary="curl https://example.com",
            decision=_ask_decision(),
            created_at=created_at,
            expires_at=expires_at,
        )

    with pytest.raises(ValueError, match="tool_name"):
        ApprovalRequest(
            request_id="req-1",
            tool_name="",
            command_summary="curl https://example.com",
            decision=_ask_decision(),
            created_at=created_at,
            expires_at=expires_at,
        )

    with pytest.raises(ValueError, match="expires_at"):
        ApprovalRequest(
            request_id="req-1",
            tool_name="run_command",
            command_summary="curl https://example.com",
            decision=_ask_decision(),
            created_at=created_at,
            expires_at=created_at,
        )


def test_approval_decision_rejects_empty_request_id() -> None:
    """审批结果不能脱离有效的审批请求身份。"""
    with pytest.raises(ValueError, match="request_id"):
        ApprovalDecision.approve(request_id="", user_reason="ok")
