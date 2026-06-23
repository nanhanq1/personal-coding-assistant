"""权限策略判断。

修改前旧代码：
权限策略占位模块，计划在第 3 周实现。

问题：风险分类已经能产出 RiskAssessment，但还没有独立策略层把风险映射为执行动作。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pca.permissions.risk import RiskAssessment, RiskLevel


class DecisionAction(Enum):
    """权限策略对一次工具调用给出的执行动作。"""

    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


@dataclass(frozen=True)
class PermissionDecision:
    """一次权限策略判断的结构化结果。"""

    action: DecisionAction
    reason: str
    assessment: RiskAssessment


class PermissionPolicy:
    """把风险评估转换为策略动作，不负责执行命令。"""

    def decide(self, assessment: RiskAssessment) -> PermissionDecision:
        """根据风险等级返回最小权限决策。"""
        if not isinstance(assessment, RiskAssessment):
            raise TypeError("assessment must be a RiskAssessment")

        if assessment.level is RiskLevel.SAFE:
            return PermissionDecision(
                action=DecisionAction.ALLOW,
                reason="Safe risk assessments are allowed by the default policy.",
                assessment=assessment,
            )
        if assessment.level is RiskLevel.ASK:
            return PermissionDecision(
                action=DecisionAction.ASK,
                reason="Ask risk assessments require approval before execution.",
                assessment=assessment,
            )
        if assessment.level is RiskLevel.DENY:
            return PermissionDecision(
                action=DecisionAction.DENY,
                reason="Deny risk assessments are blocked by the default policy.",
                assessment=assessment,
            )
        raise ValueError(f"unsupported risk level: {assessment.level!r}")


__all__ = ["DecisionAction", "PermissionDecision", "PermissionPolicy"]
