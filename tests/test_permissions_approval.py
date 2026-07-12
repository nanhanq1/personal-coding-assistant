from datetime import datetime, timedelta, timezone, tzinfo

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


class _FoldAwareTimezone(tzinfo):
    """最小 fold-aware 时区，避免测试依赖宿主机 tzdata。"""

    def utcoffset(self, value: datetime | None) -> timedelta:
        return timedelta(hours=-5 if value is not None and value.fold else -4)

    def dst(self, value: datetime | None) -> timedelta:
        return timedelta(hours=-1 if value is not None and value.fold else 0)

    def tzname(self, value: datetime | None) -> str:
        return "TEST-FOLD"


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


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("request_id", 1),
        ("tool_name", None),
        ("command_summary", []),
    ],
)
def test_approval_request_rejects_non_string_identity_fields(
    field_name: str,
    invalid_value: object,
) -> None:
    """审批请求字符串字段的错误类型必须稳定为 TypeError。"""
    created_at = datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc)
    arguments = {
        "request_id": "req-1",
        "tool_name": "run_command",
        "command_summary": "curl https://example.com",
        "decision": _ask_decision(),
        "created_at": created_at,
        "expires_at": created_at + timedelta(minutes=5),
    }
    arguments[field_name] = invalid_value

    with pytest.raises(TypeError, match=field_name):
        ApprovalRequest(**arguments)


@pytest.mark.parametrize("field_name", ["request_id", "tool_name", "command_summary"])
def test_approval_request_rejects_whitespace_identity_fields(field_name: str) -> None:
    """只含空白的审批请求字段不能成为有效身份或摘要。"""
    created_at = datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc)
    arguments = {
        "request_id": "req-1",
        "tool_name": "run_command",
        "command_summary": "curl https://example.com",
        "decision": _ask_decision(),
        "created_at": created_at,
        "expires_at": created_at + timedelta(minutes=5),
    }
    arguments[field_name] = "   "

    with pytest.raises(ValueError, match=field_name):
        ApprovalRequest(**arguments)


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_exception"),
    [
        ("created_at", "now", TypeError),
        ("expires_at", "later", TypeError),
        ("created_at", datetime(2026, 6, 22, 9, 0), ValueError),
        ("expires_at", datetime(2026, 6, 22, 9, 5), ValueError),
    ],
)
def test_approval_request_requires_aware_datetimes(
    field_name: str,
    invalid_value: object,
    expected_exception: type[Exception],
) -> None:
    """审批有效期只接受可比较的带时区 datetime。"""
    created_at = datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc)
    arguments = {
        "request_id": "req-1",
        "tool_name": "run_command",
        "command_summary": "curl https://example.com",
        "decision": _ask_decision(),
        "created_at": created_at,
        "expires_at": created_at + timedelta(minutes=5),
    }
    arguments[field_name] = invalid_value

    with pytest.raises(expected_exception, match=field_name):
        ApprovalRequest(**arguments)


@pytest.mark.parametrize(
    ("factory", "invalid_value", "expected_exception", "field_name"),
    [
        (ApprovalDecision.approve, 1, TypeError, "request_id"),
        (ApprovalDecision.reject, None, TypeError, "request_id"),
        (ApprovalDecision.approve, "   ", ValueError, "request_id"),
    ],
)
def test_approval_decision_factories_validate_request_id(
    factory,
    invalid_value: object,
    expected_exception: type[Exception],
    field_name: str,
) -> None:
    """approve/reject 工厂必须继承构造器的稳定身份校验。"""
    with pytest.raises(expected_exception, match=field_name):
        factory(request_id=invalid_value, user_reason="because")


def test_approval_decision_requires_bool_reason_and_aware_time() -> None:
    """审批结果拒绝整数布尔、非字符串理由和无时区时间。"""
    with pytest.raises(TypeError, match="approved"):
        ApprovalDecision(request_id="req-1", approved=1, user_reason="because")
    with pytest.raises(TypeError, match="user_reason"):
        ApprovalDecision(request_id="req-1", approved=True, user_reason=None)
    with pytest.raises(ValueError, match="user_reason"):
        ApprovalDecision(request_id="req-1", approved=True, user_reason="   ")
    with pytest.raises(TypeError, match="decided_at"):
        ApprovalDecision(
            request_id="req-1",
            approved=True,
            user_reason="because",
            decided_at="now",
        )
    with pytest.raises(ValueError, match="decided_at"):
        ApprovalDecision(
            request_id="req-1",
            approved=True,
            user_reason="because",
            decided_at=datetime(2026, 6, 22, 9, 0),
        )


def test_approval_request_is_expired_validates_now_and_accepts_aware_offset() -> None:
    """过期判断拒绝错误时间，同时允许任意带时区 datetime。"""
    created_at = datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc)
    request = ApprovalRequest(
        request_id="req-1",
        tool_name="run_command",
        command_summary="curl https://example.com",
        decision=_ask_decision(),
        created_at=created_at,
        expires_at=created_at + timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="now"):
        request.is_expired("now")
    with pytest.raises(ValueError, match="now"):
        request.is_expired(datetime(2026, 6, 22, 9, 5))

    utc_plus_eight = timezone(timedelta(hours=8))
    assert request.is_expired(datetime(2026, 6, 22, 17, 5, tzinfo=utc_plus_eight))


def test_approval_times_compare_absolute_instants_across_dst_fold() -> None:
    """DST 回拨的重复墙上时间必须按 UTC 绝对时刻比较。"""
    fold_timezone = _FoldAwareTimezone()
    created_at = datetime(2026, 11, 1, 1, 30, tzinfo=fold_timezone, fold=0)
    expires_at = datetime(2026, 11, 1, 1, 15, tzinfo=fold_timezone, fold=1)

    request = ApprovalRequest(
        request_id="req-dst",
        tool_name="run_command",
        command_summary="echo safe",
        decision=_ask_decision(),
        created_at=created_at,
        expires_at=expires_at,
    )

    assert not request.is_expired(
        datetime(2026, 11, 1, 1, 0, tzinfo=fold_timezone, fold=1)
    )
    assert request.is_expired(expires_at)
