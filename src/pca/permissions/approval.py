"""人工审批对象。

修改前旧代码：
人工审批流程占位模块，计划在第 3 周实现。

问题：PermissionDecision(action=ASK) 只能表达策略要求询问用户，还没有可审查的审批请求和用户决策对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from pca.permissions.policy import PermissionDecision


@dataclass(frozen=True)
class ApprovalRequest:
    """一次需要人工确认的工具执行请求。"""

    request_id: str
    tool_name: str
    command_summary: str
    decision: PermissionDecision
    created_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        if self.request_id.strip() == "":
            raise ValueError("request_id must be a non-empty string")
        if self.tool_name.strip() == "":
            raise ValueError("tool_name must be a non-empty string")
        if self.command_summary.strip() == "":
            raise ValueError("command_summary must be a non-empty string")
        if not isinstance(self.decision, PermissionDecision):
            raise TypeError("decision must be a PermissionDecision")
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be later than created_at")

    def is_expired(self, now: datetime | None = None) -> bool:
        """判断审批请求在给定时间点是否已经过期。"""
        current_time = now if now is not None else datetime.now(timezone.utc)
        return current_time >= self.expires_at


@dataclass(frozen=True)
class ApprovalDecision:
    """用户对某个审批请求做出的批准或拒绝。"""

    request_id: str
    approved: bool
    user_reason: str
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.request_id.strip() == "":
            raise ValueError("request_id must be a non-empty string")
        if self.user_reason.strip() == "":
            raise ValueError("user_reason must be a non-empty string")

    @classmethod
    def approve(
        cls,
        request_id: str,
        user_reason: str,
        decided_at: datetime | None = None,
    ) -> "ApprovalDecision":
        """创建批准结果，不负责执行命令。"""
        return cls(
            request_id=request_id,
            approved=True,
            user_reason=user_reason,
            decided_at=decided_at or datetime.now(timezone.utc),
        )

    @classmethod
    def reject(
        cls,
        request_id: str,
        user_reason: str,
        decided_at: datetime | None = None,
    ) -> "ApprovalDecision":
        """创建拒绝结果，不负责写审计。"""
        return cls(
            request_id=request_id,
            approved=False,
            user_reason=user_reason,
            decided_at=decided_at or datetime.now(timezone.utc),
        )


__all__ = ["ApprovalRequest", "ApprovalDecision"]
