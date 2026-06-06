from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolCall:
    """assistant 请求程序执行某个工具的结构化指令。"""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """校验工具调用结构，避免 LLM 生成的坏参数进入工具层。"""
        # 修改前旧代码：
        # @dataclass(frozen=True)
        # class ToolCall:
        #     name: str
        #     arguments: dict[str, Any] = field(default_factory=dict)
        #
        # 问题：没有校验 name 和 arguments，LLM 生成的坏结构会直接进入工具系统。
        if not isinstance(self.name, str) or self.name.strip() == "":
            raise ValueError("tool call name must be a non-empty string")
        if not isinstance(self.arguments, dict):
            raise TypeError("tool call arguments must be a dictionary")


@dataclass(frozen=True)
class Message:
    """LLM、用户和工具之间共享的 message history 中的一条记录。"""

    role: Role
    content: str
    name: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    def __post_init__(self) -> None:
        """校验消息基础结构，保证 AgentLoop 轨迹可回放。"""
        # 修改前旧代码：
        # @dataclass(frozen=True)
        # class Message:
        #     role: Role
        #     content: str
        #     name: str | None = None
        #     tool_calls: list[ToolCall] = field(default_factory=list)
        #
        # 问题：没有校验 role、content、name 和 tool_calls，坏消息会破坏轨迹回放。
        if self.role not in ("system", "user", "assistant", "tool"):
            raise ValueError(f"unsupported message role: {self.role}")
        if not isinstance(self.content, str):
            raise TypeError("message content must be a string")
        if self.name is not None and (not isinstance(self.name, str) or self.name.strip() == ""):
            raise ValueError("message name must be a non-empty string when provided")
        if not isinstance(self.tool_calls, list):
            raise TypeError("message tool_calls must be a list")
        if any(not isinstance(tool_call, ToolCall) for tool_call in self.tool_calls):
            raise TypeError("message tool_calls must contain ToolCall instances")
