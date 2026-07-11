import pytest

from pca.core.agent_loop import AgentLoop
from pca.core.messages import Message, ToolCall
from pca.tools.base import Tool
from pca.tools.registry import ToolRegistry


class ScriptedLLM:
    def __init__(self):
        self.calls = 0

    def complete(self, messages):
        self.calls += 1
        if self.calls == 1:
            return Message(
                role="assistant",
                content="I need to inspect the greeting.",
                tool_calls=[ToolCall(name="echo", arguments={"text": "hello"})],
            )
        return Message(role="assistant", content="The tool said: hello")


def test_agent_loop_runs_tool_call_and_continues_to_final_answer():

    tool = Tool(name="echo", description="回显工具", handler=lambda x: x.get("text", ""))
    tool_registry = ToolRegistry()
    tool_registry.register(tool)

    loop = AgentLoop(
        llm=ScriptedLLM(),
        tools=tool_registry,
    )

    result = loop.run("Say hello")

    assert result.final_message.content == "The tool said: hello"
    assert [message.role for message in result.messages] == [
        "user",
        "assistant",
        "tool",
        "assistant",
    ]
    assert result.messages[2].name == "echo"
    assert result.messages[2].content == "hello"


def test_agent_loop_rejects_invalid_configuration():
    """测试 AgentLoop 初始化时拒绝无效最大轮数。"""
    registry = ToolRegistry()

    for invalid_max_turns in (0, -1, 1.5, "8"):
        with pytest.raises(ValueError, match="max_turns"):
            AgentLoop(llm=ScriptedLLM(), tools=registry, max_turns=invalid_max_turns)


def test_agent_loop_rejects_blank_user_input():
    """测试用户输入不能为空，避免生成无意义轨迹。"""
    loop = AgentLoop(llm=ScriptedLLM(), tools=ToolRegistry())

    with pytest.raises(ValueError, match="user_input"):
        loop.run(" ")


def test_agent_loop_requires_llm_to_return_message():
    """测试 LLM adapter 必须返回 Message 对象。"""

    class BadLLM:
        def complete(self, messages):
            return "not-a-message"

    loop = AgentLoop(llm=BadLLM(), tools=ToolRegistry())

    with pytest.raises(TypeError, match="Message"):
        loop.run("hello")


def test_agent_loop_records_tool_error_and_allows_recovery():
    """测试工具失败会写回 message history，让 LLM 有机会恢复回答。"""

    class RecoveringLLM:
        def __init__(self):
            self.calls = 0

        def complete(self, messages):
            self.calls += 1
            if self.calls == 1:
                return Message(
                    role="assistant",
                    content="I will call a missing tool.",
                    tool_calls=[ToolCall(name="missing_tool", arguments={})],
                )
            assert messages[-1].role == "tool"
            assert messages[-1].name == "missing_tool"
            assert "Tool execution failed" in messages[-1].content
            return Message(role="assistant", content="I recovered from the tool error.")

    loop = AgentLoop(llm=RecoveringLLM(), tools=ToolRegistry())

    result = loop.run("please recover")

    assert result.final_message.content == "I recovered from the tool error."


def test_agent_loop_propagates_trace_context_and_tool_call_id():
    """测试 AgentLoop 为工具调用生成 run 级 trace 和调用级 id。"""

    class RecordingRegistry(ToolRegistry):
        def __init__(self):
            super().__init__()
            self.metadata = []

        def run(self, name, arguments, *, trace_id=None, tool_call_id=None):
            self.metadata.append((trace_id, tool_call_id))
            return super().run(
                name,
                arguments,
                trace_id=trace_id,
                tool_call_id=tool_call_id,
            )

    class OneToolLLM:
        def __init__(self):
            self.calls = 0

        def complete(self, messages):
            self.calls += 1
            if self.calls == 1:
                return Message(
                    role="assistant",
                    content="call echo",
                    tool_calls=[
                        ToolCall(name="echo", arguments={}),
                        ToolCall(name="echo", arguments={}),
                    ],
                )
            return Message(role="assistant", content="done")

    registry = RecordingRegistry()
    registry.register(Tool(name="echo", description="回显", handler=lambda _: "ok"))

    result = AgentLoop(llm=OneToolLLM(), tools=registry).run("trace me")

    assert result.trace_id
    assert len(registry.metadata) == 2
    trace_ids = {metadata[0] for metadata in registry.metadata}
    tool_call_ids = [metadata[1] for metadata in registry.metadata]
    assert trace_ids == {result.trace_id}
    assert all(tool_call_ids)
    assert len(set(tool_call_ids)) == 2
