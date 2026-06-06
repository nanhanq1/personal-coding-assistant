from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolCall:
    """A structured request from the assistant to run one tool."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Message:
    """One item in the conversation history shared with the LLM."""

    role: Role
    content: str
    name: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

