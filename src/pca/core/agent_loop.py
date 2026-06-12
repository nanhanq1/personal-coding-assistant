from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pca.core.messages import Message
from pca.tools.base import ToolResult
from pca.tools.registry import ToolRegistry


class LLM(Protocol):
    """AgentLoop 依赖的最小 LLM 协议。"""

    def complete(self, messages: list[Message]) -> Message:
        """根据当前 message history 生成下一条 assistant 消息。"""


@dataclass(frozen=True)
class AgentLoopResult:
    """一次 AgentLoop 运行的最终答案和完整轨迹。"""

    final_message: Message
    messages: list[Message]


class AgentLoop:
    """最小 Coding Agent 循环：调用 LLM、执行工具、再把结果交回 LLM。"""

    def __init__(
        self,
        llm: LLM,
        tools: ToolRegistry,
        max_turns: int = 8,
    ):
        # 修改前旧代码：
        # self._llm = llm
        # self._tools = tools
        # self._max_turns = max_turns
        #
        # 问题：没有校验 llm、tools 和 max_turns，坏配置会拖到运行期才暴露。
        if not hasattr(llm, "complete") or not callable(llm.complete):
            raise TypeError("llm must provide a callable complete(messages) method")
        if not isinstance(tools, ToolRegistry):
            raise TypeError("tools must be a ToolRegistry")
        if not isinstance(max_turns, int) or isinstance(max_turns, bool) or max_turns <= 0:
            raise ValueError("max_turns must be a positive integer")

        self._llm = llm
        self._tools = tools
        self._max_turns = max_turns

    def run(self, user_input: str) -> AgentLoopResult:
        """运行到 assistant 返回不含 tool_call 的消息为止。"""
        # 修改前旧代码：
        # messages = [Message(role="user", content=user_input)]
        #
        # 问题：空字符串、None 或非字符串输入会进入 message history，后续 LLM 行为不可控。
        if not isinstance(user_input, str) or user_input.strip() == "":
            raise ValueError("user_input must be a non-empty string")

        messages = [Message(role="user", content=user_input)]

        for _ in range(self._max_turns):
            assistant_message = self._llm.complete(messages)
            # 修改前旧代码：
            # assistant_message = self._llm.complete(messages)
            # messages.append(assistant_message)
            #
            # 问题：没有确认 LLM adapter 真的返回 Message，返回字符串等坏对象会在后面 AttributeError。
            if not isinstance(assistant_message, Message):
                raise TypeError("LLM complete(...) must return a Message")

            messages.append(assistant_message)

            if not assistant_message.tool_calls:
                return AgentLoopResult(
                    final_message=assistant_message,
                    messages=messages,
                )

            for tool_call in assistant_message.tool_calls:
                # AgentLoop 只负责按 ToolCall 路由，不关心具体工具函数如何实现。
                # 修改前旧代码：
                # tool_result = self._tools.run(tool_call.name, tool_call.arguments)
                #
                # 问题：工具失败会直接中断循环，LLM 看不到错误，也没有机会恢复。
                try:
                    tool_result = self._tools.run(tool_call.name, tool_call.arguments)
                except Exception as exc:
                    # 工业级 Agent 不应因为一次工具失败直接丢失轨迹；
                    # 把错误写回 history，LLM 才有机会解释、重试或换策略。
                    tool_result = ToolResult.from_exception(exc, duration_ms=0)
                messages.append(self._tool_result_to_message(tool_call.name, tool_result))

        raise RuntimeError("Agent loop exceeded max_turns.")

    @staticmethod
    def _tool_result_to_message(tool_name: str, tool_result: ToolResult) -> Message:
        """把内部结构化工具结果转换成 LLM 可继续消费的 tool 消息。"""
        if not isinstance(tool_result, ToolResult):
            raise TypeError("tool_result must be a ToolResult")
        return Message(
            role="tool",
            name=tool_name,
            content=str(tool_result),
        )
