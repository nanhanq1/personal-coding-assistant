from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from pca.core.messages import Message


ToolFunction = Callable[[dict[str, Any]], Any]


class LLM(Protocol):
    """Minimal protocol required by AgentLoop."""

    def complete(self, messages: list[Message]) -> Message:
        """Generate the next assistant message from conversation history."""


@dataclass(frozen=True)
class AgentLoopResult:
    """The final answer and full trajectory produced by one AgentLoop run."""

    final_message: Message
    messages: list[Message]


class AgentLoop:
    """Minimal Coding Agent loop: ask LLM, run requested tools, continue."""

    def __init__(
        self,
        llm: LLM,
        tools: dict[str, ToolFunction],
        max_turns: int = 8,
    ):
        self._llm = llm
        self._tools = tools
        self._max_turns = max_turns

    def run(self, user_input: str) -> AgentLoopResult:
        """Run until the assistant returns a message without tool calls."""

        messages = [Message(role="user", content=user_input)]

        for _ in range(self._max_turns):
            assistant_message = self._llm.complete(messages)
            messages.append(assistant_message)

            if not assistant_message.tool_calls:
                return AgentLoopResult(
                    final_message=assistant_message,
                    messages=messages,
                )

            for tool_call in assistant_message.tool_calls:
                tool = self._tools.get(tool_call.name)
                if tool is None:
                    raise KeyError(f"Unknown tool: {tool_call.name}")
                tool_result = tool(tool_call.arguments)
                messages.append(
                    Message(
                        role="tool",
                        name=tool_call.name,
                        content=str(tool_result),
                    )
                )

        raise RuntimeError("Agent loop exceeded max_turns.")
