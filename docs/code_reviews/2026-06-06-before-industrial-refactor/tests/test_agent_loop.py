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
