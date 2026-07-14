"""权限审计事件。

修改前旧代码：
审计事件模块尚未实现，permission gate 只能拦截或放行，但没有稳定的
JSONL 事实记录。

问题：后续审批、sandbox、rollback 和安全回归需要可追溯证据，不能只依赖
异常消息或测试断言。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pca.permissions.policy import DecisionAction, PermissionDecision


@dataclass(frozen=True)
class PermissionAuditEvent:
    """一次权限判断的事实记录，不参与 allow / ask / deny 决策。"""

    timestamp: datetime
    operation_id: str
    tool_name: str
    action: DecisionAction
    risk_level: str
    matched_rule: str
    reason: str
    authorized: bool

    def to_dict(self) -> dict[str, Any]:
        """转换为稳定 JSON 字段，避免把 enum 或 datetime 对象直接写入文件。"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": "permission_decision",
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "action": self.action.value,
            "risk_level": self.risk_level,
            "matched_rule": self.matched_rule,
            "reason": self.reason,
            "authorized": self.authorized,
        }


class ToolExecutionPhase(Enum):
    """副作用执行的本地生命周期阶段。"""

    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    ROLLBACK_FAILED = "rollback_failed"


@dataclass(frozen=True)
class ToolExecutionAuditEvent:
    """不含原始参数和异常详情的工具执行摘要事件。"""

    timestamp: datetime
    operation_id: str
    tool_name: str
    phase: ToolExecutionPhase

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": "tool_execution",
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "phase": self.phase.value,
        }


class AuditPersistenceError(RuntimeError):
    """副作用路径中的审计结果无法持久化。"""

    def __init__(
        self,
        *,
        phase: ToolExecutionPhase | str,
        side_effect_state: str,
    ) -> None:
        self.phase = phase
        self.side_effect_state = side_effect_state
        phase_value = phase.value if isinstance(phase, ToolExecutionPhase) else phase
        super().__init__(
            "audit persistence failed after tool phase "
            f"{phase_value}; side_effect_state={side_effect_state}"
        )


def append_audit_event(
    path: Path,
    event: PermissionAuditEvent | ToolExecutionAuditEvent,
) -> None:
    """把权限审计事件追加为一行 JSONL。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event.to_dict(), ensure_ascii=False))
        file.write("\n")


def record_permission_decision(
    path: Path,
    operation_id: str,
    tool_name: str,
    decision: PermissionDecision,
    *,
    authorized: bool,
) -> None:
    """把一次 gate 决策写为摘要审计事件，不接收原始工具参数。"""
    event = PermissionAuditEvent(
        timestamp=datetime.now(timezone.utc),
        operation_id=operation_id,
        tool_name=tool_name,
        action=decision.action,
        risk_level=decision.assessment.level.value,
        matched_rule=decision.assessment.matched_rule,
        reason=decision.reason,
        authorized=authorized,
    )
    append_audit_event(path, event)


def record_tool_execution_event(
    path: Path,
    *,
    operation_id: str,
    tool_name: str,
    phase: ToolExecutionPhase,
) -> None:
    """追加不含原始输入的工具执行阶段。"""
    append_audit_event(
        path,
        ToolExecutionAuditEvent(
            timestamp=datetime.now(timezone.utc),
            operation_id=operation_id,
            tool_name=tool_name,
            phase=phase,
        ),
    )


def new_operation_id() -> str:
    """为一次 wrapper 调用生成本地关联 id。"""
    return uuid4().hex


__all__ = [
    "PermissionAuditEvent",
    "ToolExecutionAuditEvent",
    "ToolExecutionPhase",
    "AuditPersistenceError",
    "append_audit_event",
    "record_permission_decision",
    "record_tool_execution_event",
    "new_operation_id",
]
