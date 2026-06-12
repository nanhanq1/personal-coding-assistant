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


class EditThenReadLLM:
    """脚本化模拟：先局部编辑文件，再读回验证结果。"""

    def __init__(self, workspace_root: str) -> None:
        self._workspace_root = workspace_root
        self._calls = 0

    def complete(self, messages):
        self._calls += 1

        if self._calls == 1:
            return Message(
                role="assistant",
                content="I will update the note with edit_file.",
                tool_calls=[
                    ToolCall(
                        name="edit_file",
                        arguments={
                            "path": "notes/day5.txt",
                            "old_text": "status: draft",
                            "new_text": "status: verified",
                            "workspace_root": self._workspace_root,
                        },
                    )
                ],
            )

        if self._calls == 2:
            assert messages[-1].role == "tool"
            assert messages[-1].name == "edit_file"
            assert messages[-1].content == "ok"
            return Message(
                role="assistant",
                content="I will read the edited note.",
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
        assert messages[-1].content == "status: verified"
        return Message(role="assistant", content="The note was edited and verified.")


def test_agent_loop_integrates_edit_file_schema_and_structured_success_result(tmp_path):
    """测试 schema、edit_file 和 ToolResult 成功链路能被 AgentLoop 串起来。"""
    note_path = tmp_path / "notes" / "day5.txt"
    note_path.parent.mkdir()
    note_path.write_text("status: draft", encoding="utf-8")
    registry = create_coding_tool_registry()

    schemas_by_name = {
        schema["name"]: schema
        for schema in registry.list_tool_schemas()
    }

    assert "edit_file" in schemas_by_name
    assert schemas_by_name["edit_file"]["parameters"]["required"] == [
        "path",
        "old_text",
        "new_text",
    ]

    loop = AgentLoop(
        llm=EditThenReadLLM(workspace_root=str(tmp_path)),
        tools=registry,
    )

    result = loop.run("Update the Day 5 note.")

    assert result.final_message.content == "The note was edited and verified."
    assert note_path.read_text(encoding="utf-8") == "status: verified"
    assert [message.role for message in result.messages] == [
        "user",
        "assistant",
        "tool",
        "assistant",
        "tool",
        "assistant",
    ]


class FailingEditLLM:
    """脚本化模拟：触发 edit_file 失败，再基于工具错误恢复回答。"""

    def __init__(self, workspace_root: str) -> None:
        self._workspace_root = workspace_root
        self._calls = 0

    def complete(self, messages):
        self._calls += 1

        if self._calls == 1:
            return Message(
                role="assistant",
                content="I will try to edit stale text.",
                tool_calls=[
                    ToolCall(
                        name="edit_file",
                        arguments={
                            "path": "notes/day5.txt",
                            "old_text": "missing text",
                            "new_text": "replacement",
                            "workspace_root": self._workspace_root,
                        },
                    )
                ],
            )

        assert messages[-1].role == "tool"
        assert messages[-1].name == "edit_file"
        assert "Tool execution failed: ValueError: old_text was not found" == messages[-1].content
        return Message(role="assistant", content="The edit failed because the context was stale.")


def test_agent_loop_records_structured_edit_file_failure_as_tool_message(tmp_path):
    """测试 edit_file 失败会通过 ToolResult 稳定写回 tool message。"""
    note_path = tmp_path / "notes" / "day5.txt"
    note_path.parent.mkdir()
    note_path.write_text("status: draft", encoding="utf-8")

    loop = AgentLoop(
        llm=FailingEditLLM(workspace_root=str(tmp_path)),
        tools=create_coding_tool_registry(),
    )

    result = loop.run("Update stale text.")

    assert result.final_message.content == "The edit failed because the context was stale."
    assert note_path.read_text(encoding="utf-8") == "status: draft"


def test_agent_loop_exposes_tool_result_message_serializer_for_day5_boundary():
    """测试 AgentLoop 明确拥有 ToolResult 到 Message 的序列化边界。"""
    assert hasattr(AgentLoop, "_tool_result_to_message")
