"""人工审批对象。

修改前旧代码：
人工审批流程占位模块，计划在第 3 周实现。

问题：PermissionDecision(action=ASK) 只能表达策略要求询问用户，还没有可审查的审批请求和用户决策对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from pca.permissions.policy import PermissionDecision


def _validate_non_empty_string(field_name: str, value: object) -> None:
    """为公开 approval 字符串字段提供稳定的类型与空值语义。"""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if value.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_aware_datetime(field_name: str, value: object) -> None:
    """拒绝错误类型和无时区时间，避免比较阶段泄漏偶然异常。"""
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


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
        # 修改前旧代码：
        # if self.request_id.strip() == "": ...
        # if self.tool_name.strip() == "": ...
        # if self.command_summary.strip() == "": ...
        # if self.expires_at <= self.created_at: ...
        #
        # 问题：错误类型会泄漏 AttributeError 或 datetime 比较异常，
        # naive/aware 时间混用也没有清晰契约。
        _validate_non_empty_string("request_id", self.request_id)
        _validate_non_empty_string("tool_name", self.tool_name)
        _validate_non_empty_string("command_summary", self.command_summary)
        if not isinstance(self.decision, PermissionDecision):
            raise TypeError("decision must be a PermissionDecision")
        _validate_aware_datetime("created_at", self.created_at)
        _validate_aware_datetime("expires_at", self.expires_at)
        if _as_utc(self.expires_at) <= _as_utc(self.created_at):
            raise ValueError("expires_at must be later than created_at")

    def is_expired(self, now: datetime | None = None) -> bool:
        """判断审批请求在给定时间点是否已经过期。"""
        current_time = now if now is not None else datetime.now(timezone.utc)
        _validate_aware_datetime("now", current_time)
        return _as_utc(current_time) >= _as_utc(self.expires_at)


@dataclass(frozen=True)
class ApprovalDecision:
    """用户对某个审批请求做出的批准或拒绝。"""

    request_id: str
    approved: bool
    user_reason: str
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        # 修改前旧代码：
        # if self.request_id.strip() == "": ...
        # if self.user_reason.strip() == "": ...
        #
        # 问题：非字符串触发 AttributeError，approved 和 decided_at
        # 也会接受与公开契约不一致的整数或字符串。
        _validate_non_empty_string("request_id", self.request_id)
        if not isinstance(self.approved, bool):
            raise TypeError("approved must be a boolean")
        _validate_non_empty_string("user_reason", self.user_reason)
        _validate_aware_datetime("decided_at", self.decided_at)

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


def _as_utc(value: datetime) -> datetime:
    """按绝对时刻比较 aware datetime，避免同 tzinfo 的 fold 墙上时间陷阱。"""
    return value.astimezone(timezone.utc)
