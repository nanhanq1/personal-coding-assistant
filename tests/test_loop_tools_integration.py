from pca.core.agent_loop import AgentLoop
from pca.core.messages import Message, ToolCall
from pca.tools import create_coding_tool_registry


class WriteThenReadLLM:
    """脚本化模拟：先写文件，再读文件，最后基于工具结果回答。"""

    def __init__(self, workspace_root: str) -> None:
        self._workspace_root = workspace_root
        self._calls = 0

    def complete(self, messages):
        self._calls += 1

        if self._calls == 1:
            return Message(
                role="assistant",
                content="I will create the note first.",
                tool_calls=[
                    ToolCall(
                        name="write_file",
                        arguments={
                            "path": "notes/day5.txt",
                            "content": "Day 5 connects loop and tools.",
                            "workspace_root": self._workspace_root,
                        },
                    )
                ],
            )

        if self._calls == 2:
            assert messages[-1].role == "tool"
            assert messages[-1].name == "write_file"
            assert messages[-1].content == "ok"
            return Message(
                role="assistant",
                content="I will read the note back.",
                tool_calls=[
                    ToolCall(
                        name="read_file",
                        arguments={
                            "path": "notes/day5.txt",
                            "workspace_root": self._workspace_root,
                        },
                    )
                ],
            )

        assert messages[-1].role == "tool"
        assert messages[-1].name == "read_file"
        assert messages[-1].content == "Day 5 connects loop and tools."
        return Message(role="assistant", content="The note was created and verified.")


def test_agent_loop_uses_default_coding_tools_for_write_then_read(tmp_path):
    """测试 AgentLoop 能通过默认工具注册表连续路由多个不同工具。"""
    loop = AgentLoop(
        llm=WriteThenReadLLM(workspace_root=str(tmp_path)),
        tools=create_coding_tool_registry(),
    )

    result = loop.run("Create a Day 5 note and verify it.")

    assert result.final_message.content == "The note was created and verified."
    assert [message.role for message in result.messages] == [
        "user",
        "assistant",
        "tool",
        "assistant",
        "tool",
        "assistant",
    ]
    assert result.messages[2].name == "write_file"
    assert result.messages[4].name == "read_file"
