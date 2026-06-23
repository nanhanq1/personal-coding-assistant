import pytest

from pca.permissions.policy import DecisionAction, PermissionPolicy
from pca.permissions.risk import RiskAssessment, RiskLevel


def test_policy_allows_safe_assessment() -> None:
    """SAFE 风险评估应被策略映射为 ALLOW。"""
    assessment = RiskAssessment(
        level=RiskLevel.SAFE,
        reason="Command appears read-only.",
        matched_rule="default_safe",
    )

    decision = PermissionPolicy().decide(assessment)

    assert decision.action is DecisionAction.ALLOW
    assert decision.assessment is assessment
    assert decision.reason


def test_policy_asks_for_ask_assessment() -> None:
    """ASK 风险评估应被策略映射为 ASK，交给后续审批层处理。"""
    assessment = RiskAssessment(
        level=RiskLevel.ASK,
        reason="Network commands can read from or write to external systems.",
        matched_rule="network_access",
    )

    decision = PermissionPolicy().decide(assessment)

    assert decision.action is DecisionAction.ASK
    assert decision.assessment is assessment
    assert decision.reason


def test_policy_denies_deny_assessment() -> None:
    """DENY 风险评估应被策略映射为 DENY，不进入执行链。"""
    assessment = RiskAssessment(
        level=RiskLevel.DENY,
        reason="Recursive delete commands are destructive.",
        matched_rule="recursive_delete",
    )

    decision = PermissionPolicy().decide(assessment)

    assert decision.action is DecisionAction.DENY
    assert decision.assessment is assessment
    assert decision.reason


def test_policy_rejects_non_risk_assessment() -> None:
    """策略层只接收风险分类结果，不能直接接收原始命令或任意对象。"""
    with pytest.raises(TypeError, match="RiskAssessment"):
        PermissionPolicy().decide("git status")  # type: ignore[arg-type]
