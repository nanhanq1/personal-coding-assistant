from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class TraceContext:
    """一次 Agent 调用链共享的 trace 上下文。"""

    trace_id: str

    @classmethod
    def new(cls) -> "TraceContext":
        """生成新的 trace 上下文，供一次 Agent 运行向下传递。"""
        return cls(trace_id=uuid4().hex)


@dataclass(frozen=True)
class AgentEvent:
    """Agent 运行过程中可记录、可回放的一条轻量事件。"""

    event_type: str
    trace_id: str
    payload: dict[str, object]
