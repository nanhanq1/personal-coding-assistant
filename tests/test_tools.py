"""测试工具注册表功能"""
from typing import Any

import pytest
from pca.tools import base as tool_base
from pca.tools import create_coding_tool_registry
from pca import tools as tools_package
from pca.tools.base import Tool, ToolParameter, ToolResult
from pca.tools.registry import ToolRegistry


def test_tool_registry_basic_operations():
    """测试基本操作：注册、获取、执行"""
    registry = ToolRegistry()

    # 创建一个简单的工具
    def echo_handler(arguments: dict[str, Any]) -> Any:
        return arguments.get("text", "")

    tool = Tool(name="echo", description="回显工具", handler=echo_handler)

    # 1. 注册工具
    registry.register(tool)

    # 2. 按名称获取工具
    retrieved_tool = registry.get("echo")
    assert retrieved_tool.name == "echo"
    assert retrieved_tool.description == "回显工具"

    # 3. 执行工具
    result = registry.run("echo", {"text": "hello"})
    assert result.ok is True
    assert result.result == "hello"

    # 4. 检查工具是否存在
    assert registry.exists("echo") is True
    assert registry.exists("nonexistent") is False

    # 5. 列出所有工具
    assert registry.list_tools() == ["echo"]


def test_duplicate_registration_raises_keyerror():
    """测试重复注册同名工具会报 KeyError"""
    registry = ToolRegistry()

    def handler(arguments: dict[str, Any]) -> Any:
        return "test"

    tool1 = Tool(name="test", description="测试工具1", handler=handler)
    tool2 = Tool(name="test", description="测试工具2", handler=handler)

    # 第一次注册应该成功
    registry.register(tool1)

    # 第二次注册应该抛出 KeyError
    with pytest.raises(KeyError, match="Duplicate tool: test"):
        registry.register(tool2)


def test_run_nonexistent_tool_returns_structured_failure():
    """测试执行不存在的工具会返回结构化失败结果。"""
    registry = ToolRegistry()

    result = registry.run("nonexistent", {})

    assert result.ok is False
    assert result.result is None
    assert result.error_type == "KeyError"
    assert "Unknown tool: nonexistent" in result.error_message
    assert result.duration_ms >= 0


def test_get_nonexistent_tool_raises_keyerror():
    """测试获取不存在的工具会报 KeyError"""
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Unknown tool: nonexistent"):
        registry.get("nonexistent")


def test_unregister_tool():
    """测试注销工具"""
    registry = ToolRegistry()

    def handler(arguments: dict[str, Any]) -> Any:
        return "test"

    tool = Tool(name="test", description="测试工具", handler=handler)
    registry.register(tool)

    # 注销前应该存在
    assert registry.exists("test") is True

    # 注销工具
    registry.unregister("test")

    # 注销后应该不存在
    assert registry.exists("test") is False

    # 再次注销应该抛出 KeyError
    with pytest.raises(KeyError, match="Unknown tool: test"):
        registry.unregister("test")


def test_clear_tools():
    """测试清空所有工具"""
    registry = ToolRegistry()

    def handler(arguments: dict[str, Any]) -> Any:
        return "test"

    # 注册多个工具
    for i in range(3):
        tool = Tool(name=f"tool{i}", description=f"工具{i}", handler=handler)
        registry.register(tool)

    # 清空前应该有3个工具
    assert len(registry.list_tools()) == 3

    # 清空工具
    registry.clear()

    # 清空后应该没有工具
    assert len(registry.list_tools()) == 0


def test_tool_rejects_invalid_metadata():
    """测试工具元数据必须可被 Agent 安全展示和路由。"""

    def handler(arguments: dict[str, Any]) -> str:
        return "ok"

    for invalid_name in ("", " ", 123):
        with pytest.raises(ValueError, match="name"):
            Tool(name=invalid_name, description="描述", handler=handler)

    for invalid_description in ("", " ", None):
        with pytest.raises(ValueError, match="description"):
            Tool(name="valid_name", description=invalid_description, handler=handler)

    with pytest.raises(TypeError, match="handler"):
        Tool(name="valid_name", description="描述", handler="not-callable")


def test_tool_run_rejects_non_dict_arguments():
    """测试工具入口只接受结构化字典参数。"""

    tool = Tool(name="echo", description="回显工具", handler=lambda arguments: arguments)

    with pytest.raises(TypeError, match="arguments"):
        tool.run("not-a-dict")


def test_tool_registry_rejects_invalid_tool_instances():
    """测试注册表拒绝非 Tool 对象，避免运行期路由崩溃。"""
    registry = ToolRegistry()

    with pytest.raises(TypeError, match="Tool"):
        registry.register("not-a-tool")


def test_tool_parameter_schema_is_exported_for_llm_tool_descriptions():
    """测试 Tool 能把参数 schema 导出为接近 JSON Schema 的结构。"""
    tool = Tool(
        name="read_file",
        description="读取文件",
        handler=lambda arguments: "ok",
        parameters=(
            ToolParameter(name="path", type="string", description="文件路径"),
            ToolParameter(
                name="workspace_root",
                type="string",
                description="工作区根目录",
                required=False,
            ),
        ),
    )

    schema = tool.to_schema()

    assert schema == {
        "name": "read_file",
        "description": "读取文件",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "workspace_root": {"type": "string", "description": "工作区根目录"},
            },
            "required": ["path"],
            "additionalProperties": True,
        },
    }


def test_tool_run_validates_required_parameters_before_handler_runs():
    """测试缺少必填参数会在 Tool 层失败，不进入具体工具 handler。"""
    called = False

    def handler(arguments: dict[str, Any]) -> str:
        nonlocal called
        called = True
        return "ok"

    tool = Tool(
        name="write_file",
        description="写入文件",
        handler=handler,
        parameters=(ToolParameter(name="path", type="string", description="文件路径"),),
    )

    with pytest.raises(ValueError, match="Missing required argument: path"):
        tool.run({})

    assert called is False


def test_tool_run_validates_parameter_types_before_handler_runs():
    """测试参数类型错误会在 Tool 层失败，避免坏参数下沉到具体工具。"""
    called = False

    def handler(arguments: dict[str, Any]) -> str:
        nonlocal called
        called = True
        return "ok"

    tool = Tool(
        name="write_file",
        description="写入文件",
        handler=handler,
        parameters=(ToolParameter(name="path", type="string", description="文件路径"),),
    )

    with pytest.raises(TypeError, match="path"):
        tool.run({"path": 123})

    assert called is False


def test_tool_parameter_rejects_bool_for_number_types():
    """测试 bool 不能被当作 JSON number / integer 参数。"""
    for json_type in ("number", "integer"):
        parameter = ToolParameter(name="count", type=json_type, description="数量")

        with pytest.raises(TypeError, match="count"):
            parameter.validate({"count": True})


def test_tool_registry_exports_registered_tool_schemas():
    """测试注册表能统一导出所有工具 schema，供后续真实 LLM adapter 使用。"""
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="echo",
            description="回显",
            handler=lambda arguments: arguments["text"],
            parameters=(ToolParameter(name="text", type="string", description="文本"),),
        )
    )

    schemas = registry.list_tool_schemas()

    assert schemas == [
        {
            "name": "echo",
            "description": "回显",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "文本"},
                },
                "required": ["text"],
                "additionalProperties": True,
            },
        }
    ]


def test_tool_result_success_carries_result_and_duration():
    """测试成功 ToolResult 能稳定表达结果和耗时。"""
    result = ToolResult.success(result={"stdout": "ok"}, duration_ms=12)

    assert result.ok is True
    assert result.result == {"stdout": "ok"}
    assert result.error_type is None
    assert result.error_message is None
    assert result.duration_ms == 12
    assert result.trace_id is None
    assert result.tool_call_id is None
    assert result.output_truncated is False
    assert result.error_code is None


def test_tool_result_failure_carries_error_and_duration():
    """测试失败 ToolResult 能稳定表达错误类型、错误消息和耗时。"""
    result = ToolResult.failure(
        error_type="ValueError",
        error_message="bad argument",
        duration_ms=3,
    )

    assert result.ok is False
    assert result.result is None
    assert result.error_type == "ValueError"
    assert result.error_message == "bad argument"
    assert result.duration_ms == 3
    assert result.trace_id is None
    assert result.tool_call_id is None
    assert result.output_truncated is False
    assert result.error_code is tool_base.ToolErrorCode.RUNTIME_FAILED


def test_tool_result_failure_can_carry_stable_error_code_without_changing_text():
    """测试失败结果能携带稳定错误码，同时旧文本输出保持兼容。"""
    result = ToolResult.failure(
        error_type="PermissionError",
        error_message="approval required",
        duration_ms=3,
        error_code=tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
    )

    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert str(result) == "Tool execution failed: PermissionError: approval required"


def test_tool_result_direct_failed_construction_gets_default_error_code():
    """测试旧的 dataclass 直接构造失败结果仍保持兼容。"""
    result = ToolResult(
        ok=False,
        error_type="RuntimeError",
        error_message="boom",
    )

    assert result.error_code is tool_base.ToolErrorCode.RUNTIME_FAILED


def test_tool_error_code_is_exported_from_tools_package():
    """测试 ToolErrorCode 和 ToolResult 一样属于工具结果公开契约。"""
    assert tools_package.ToolErrorCode is tool_base.ToolErrorCode


def test_tool_result_rejects_string_error_code_to_keep_contract_stable():
    """测试 error_code 必须是 ToolErrorCode，避免散落自由字符串。"""
    with pytest.raises(TypeError, match="error_code"):
        ToolResult.failure(
            error_type="RuntimeError",
            error_message="boom",
            duration_ms=0,
            error_code="runtime_failed",  # type: ignore[arg-type]
        )


def test_tool_result_from_exception_maps_builtin_failures_to_error_codes():
    """测试常见异常会映射为稳定错误码，供后续 retry/audit/safety 使用。"""
    assert (
        ToolResult.from_exception(ValueError("bad argument"), duration_ms=0).error_code
        is tool_base.ToolErrorCode.INVALID_ARGUMENT
    )
    assert (
        ToolResult.from_exception(TypeError("bad type"), duration_ms=0).error_code
        is tool_base.ToolErrorCode.INVALID_ARGUMENT
    )
    assert (
        ToolResult.from_exception(KeyError("missing"), duration_ms=0).error_code
        is tool_base.ToolErrorCode.UNKNOWN_TOOL
    )
    assert (
        ToolResult.from_exception(RuntimeError("boom"), duration_ms=0).error_code
        is tool_base.ToolErrorCode.RUNTIME_FAILED
    )


def test_tool_result_from_exception_maps_audit_failure_to_error_code():
    from pca.permissions.audit import AuditPersistenceError, ToolExecutionPhase

    result = ToolResult.from_exception(
        AuditPersistenceError(
            phase=ToolExecutionPhase.SUCCEEDED,
            side_effect_state="completed",
        ),
        duration_ms=0,
    )

    assert result.error_code is tool_base.ToolErrorCode.AUDIT_FAILED


def test_tool_result_from_exception_maps_checkpoint_failures_to_error_code():
    """测试 checkpoint/git checkpoint 失败能区别于普通参数或 runtime 失败。"""
    assert (
        ToolResult.from_exception(
            ValueError("workspace is not a git repository: repo"),
            duration_ms=0,
        ).error_code
        is tool_base.ToolErrorCode.CHECKPOINT_FAILED
    )
    assert (
        ToolResult.from_exception(
            RuntimeError("git executable is not available"),
            duration_ms=0,
        ).error_code
        is tool_base.ToolErrorCode.CHECKPOINT_FAILED
    )


def test_tool_result_old_factories_keep_text_compatibility():
    """测试旧的 success/failure 构造方式不改变 message history 文本。"""
    success = ToolResult.success(result="ok", duration_ms=12)
    failure = ToolResult.failure(
        error_type="ValueError",
        error_message="bad argument",
        duration_ms=3,
    )

    assert str(success) == "ok"
    assert str(failure) == "Tool execution failed: ValueError: bad argument"


def test_tool_result_carries_trace_metadata_without_changing_text_output():
    """测试 ToolResult 可以携带 trace 元数据，但字符串输出保持兼容。"""
    result = ToolResult.success(
        result="done",
        duration_ms=5,
        trace_id="trace-1",
        tool_call_id="tool-call-1",
        output_truncated=True,
    )

    assert result.trace_id == "trace-1"
    assert result.tool_call_id == "tool-call-1"
    assert result.output_truncated is True
    assert str(result) == "done"


def test_tool_registry_run_returns_structured_success_result():
    """测试 ToolRegistry.run 成功时返回结构化结果，而不是裸 handler 返回值。"""
    registry = ToolRegistry()
    tool = Tool(
        name="echo",
        description="回显",
        handler=lambda arguments: arguments["text"],
        parameters=(ToolParameter(name="text", type="string", description="文本"),),
    )
    registry.register(tool)

    result = registry.run("echo", {"text": "hello"})

    assert result.ok is True
    assert result.result == "hello"
    assert result.error_type is None
    assert result.error_message is None
    assert result.duration_ms >= 0


def test_tool_registry_run_preserves_trace_metadata_on_success_and_failure():
    """测试成功和失败结果都保留调用链 trace 元数据。"""
    registry = ToolRegistry()
    registry.register(Tool(name="echo", description="回显", handler=lambda _: "ok"))

    success = registry.run(
        "echo",
        {},
        trace_id="trace-1",
        tool_call_id="call-1",
    )
    failure = registry.run(
        "missing_tool",
        {},
        trace_id="trace-1",
        tool_call_id="call-2",
    )

    assert success.trace_id == "trace-1"
    assert success.tool_call_id == "call-1"
    assert failure.trace_id == "trace-1"
    assert failure.tool_call_id == "call-2"


def test_tool_registry_run_returns_structured_failure_when_handler_raises():
    """测试 handler 抛异常时 ToolRegistry.run 返回结构化失败结果。"""

    def handler(arguments: dict[str, Any]) -> str:
        raise RuntimeError("boom")

    registry = ToolRegistry()
    tool = Tool(name="explode", description="失败工具", handler=handler)
    registry.register(tool)

    result = registry.run("explode", {})

    assert result.ok is False
    assert result.result is None
    assert result.error_type == "RuntimeError"
    assert result.error_message == "boom"
    assert result.error_code is tool_base.ToolErrorCode.RUNTIME_FAILED
    assert result.duration_ms >= 0


def test_tool_registry_run_returns_structured_failure_for_bad_arguments():
    """测试参数校验失败时 ToolRegistry.run 返回结构化失败结果。"""
    called = False

    def handler(arguments: dict[str, Any]) -> str:
        nonlocal called
        called = True
        return "ok"

    registry = ToolRegistry()
    registry.register(
        Tool(
            name="write_file",
            description="写入文件",
            handler=handler,
            parameters=(ToolParameter(name="path", type="string", description="文件路径"),),
        )
    )

    result = registry.run("write_file", {})

    assert called is False
    assert result.ok is False
    assert result.result is None
    assert result.error_type == "ValueError"
    assert "Missing required argument: path" in result.error_message
    assert result.error_code is tool_base.ToolErrorCode.INVALID_ARGUMENT
    assert result.duration_ms >= 0


def test_tool_registry_stats_records_successful_calls():
    """测试成功调用会更新 ToolRegistry 的工具统计。"""
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="echo",
            description="回显",
            handler=lambda arguments: arguments["text"],
            parameters=(ToolParameter(name="text", type="string", description="文本"),),
        )
    )

    result = registry.run("echo", {"text": "hello"})

    stats = registry.get_stats()
    assert result.ok is True
    assert stats["echo"]["calls"] == 1
    assert stats["echo"]["successes"] == 1
    assert stats["echo"]["failures"] == 0
    assert stats["echo"]["total_duration_ms"] >= result.duration_ms


def test_tool_registry_stats_records_handler_failures():
    """测试 handler 抛异常时也会更新 ToolRegistry 的工具统计。"""

    def handler(arguments: dict[str, Any]) -> str:
        raise RuntimeError("boom")

    registry = ToolRegistry()
    registry.register(Tool(name="explode", description="失败工具", handler=handler))

    result = registry.run("explode", {})

    stats = registry.get_stats()
    assert result.ok is False
    assert stats["explode"]["calls"] == 1
    assert stats["explode"]["successes"] == 0
    assert stats["explode"]["failures"] == 1
    assert stats["explode"]["total_duration_ms"] >= result.duration_ms


def test_tool_registry_stats_records_argument_failures_without_calling_handler():
    """测试参数校验失败会记录失败统计，同时不会进入 handler。"""
    called = False

    def handler(arguments: dict[str, Any]) -> str:
        nonlocal called
        called = True
        return "ok"

    registry = ToolRegistry()
    registry.register(
        Tool(
            name="write_file",
            description="写入文件",
            handler=handler,
            parameters=(ToolParameter(name="path", type="string", description="文件路径"),),
        )
    )

    result = registry.run("write_file", {})

    stats = registry.get_stats()
    assert called is False
    assert result.ok is False
    assert stats["write_file"]["calls"] == 1
    assert stats["write_file"]["successes"] == 0
    assert stats["write_file"]["failures"] == 1
    assert stats["write_file"]["total_duration_ms"] >= result.duration_ms


def test_tool_registry_stats_records_unknown_tool_failures():
    """测试未知工具调用会按请求的工具名记录失败统计。"""
    registry = ToolRegistry()

    result = registry.run("missing_tool", {})

    stats = registry.get_stats()
    assert result.ok is False
    assert result.error_type == "KeyError"
    assert result.error_code is tool_base.ToolErrorCode.UNKNOWN_TOOL
    assert stats["missing_tool"]["calls"] == 1
    assert stats["missing_tool"]["successes"] == 0
    assert stats["missing_tool"]["failures"] == 1
    assert stats["missing_tool"]["total_duration_ms"] >= result.duration_ms


@pytest.mark.parametrize(
    ("name", "expected_error_type"),
    [
        ([], "ValueError"),
        ({}, "ValueError"),
        (None, "ValueError"),
        ("", "ValueError"),
        ("   ", "ValueError"),
    ],
)
def test_tool_registry_run_returns_stable_failure_for_invalid_tool_name(
    name: Any,
    expected_error_type: str,
) -> None:
    """非法工具名也必须留在 ToolResult 信封和有界统计桶中。"""
    registry = ToolRegistry()

    result = registry.run(
        name,
        {},
        trace_id="trace-invalid-name",
        tool_call_id="call-invalid-name",
    )

    assert result.ok is False
    assert result.error_type == expected_error_type
    assert result.error_code is tool_base.ToolErrorCode.INVALID_ARGUMENT
    assert result.trace_id == "trace-invalid-name"
    assert result.tool_call_id == "call-invalid-name"
    assert registry.get_stats() == {
        "<invalid-tool-name>": {
            "calls": 1,
            "successes": 0,
            "failures": 1,
            "total_duration_ms": result.duration_ms,
        }
    }


@pytest.mark.parametrize(
    ("trace_id", "tool_call_id"),
    [
        ("", "call-1"),
        (None, "   "),
        (1, "call-1"),
    ],
)
def test_tool_registry_run_returns_stable_failure_for_invalid_trace_metadata(
    trace_id: Any,
    tool_call_id: Any,
) -> None:
    """坏 trace metadata 不能让 ToolResult 构造再次逃逸。"""
    called = False

    def handler(arguments: dict[str, Any]) -> str:
        nonlocal called
        called = True
        return "ok"

    registry = ToolRegistry()
    registry.register(Tool(name="echo", description="回显", handler=handler))

    result = registry.run(
        "echo",
        {},
        trace_id=trace_id,
        tool_call_id=tool_call_id,
    )

    assert called is False
    assert result.ok is False
    assert result.error_code is tool_base.ToolErrorCode.INVALID_ARGUMENT
    assert result.trace_id is None or result.trace_id == "call-1"
    assert result.tool_call_id is None or result.tool_call_id == "call-1"
    assert registry.get_stats()["echo"]["failures"] == 1


def test_tool_registry_rejects_reserved_invalid_stats_tool_name() -> None:
    """固定非法统计桶不能与真实工具统计发生碰撞。"""
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="reserved"):
        registry.register(
            Tool(
                name="<invalid-tool-name>",
                description="不应占用内部统计键",
                handler=lambda arguments: "ok",
            )
        )


def test_tool_registry_get_stats_returns_snapshot():
    """测试 get_stats 返回快照，外部修改不会污染注册表内部统计。"""
    registry = ToolRegistry()
    registry.register(Tool(name="echo", description="回显", handler=lambda arguments: "ok"))
    registry.run("echo", {})

    stats = registry.get_stats()
    stats["echo"]["calls"] = 999

    assert registry.get_stats()["echo"]["calls"] == 1


def test_truncate_output_keeps_short_text_unchanged():
    """测试未超过上限的输出保持原文，不误报截断。"""
    text, was_truncated = tool_base.truncate_output("small output", max_chars=20)

    assert text == "small output"
    assert was_truncated is False


def test_truncate_output_marks_large_text_with_visible_notice():
    """测试超长输出会保留前缀，并追加可见截断说明。"""
    text, was_truncated = tool_base.truncate_output("abcdef", max_chars=3)

    assert text.startswith("abc")
    assert "def" not in text
    assert "[output truncated:" in text
    assert "kept 3 of 6 chars" in text
    assert was_truncated is True


def test_tool_registry_truncates_large_shell_stdout_and_stderr():
    """测试 shell 大 stdout/stderr 会在 ToolResult 边界截断并设置元数据。"""
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="run_command",
            description="测试 shell 结果形状的工具",
            handler=lambda arguments: {
                "stdout": "O" * 5000,
                "stderr": "E" * 5000,
                "returncode": 0,
                "timed_out": False,
            },
        )
    )

    result = registry.run(
        "run_command",
        {},
    )

    stdout = result.result["stdout"]
    stderr = result.result["stderr"]

    assert result.ok is True
    assert result.output_truncated is True
    assert stdout.startswith("O" * 100)
    assert stderr.startswith("E" * 100)
    assert "kept 4000 of 5000 chars" in stdout
    assert "kept 4000 of 5000 chars" in stderr
    assert len(stdout) < 5000
    assert len(stderr) < 5000


def test_tool_registry_truncates_large_read_file_result(tmp_path):
    """测试大文件内容作为字符串 payload 返回时也会被 ToolResult 边界截断。"""
    large_file = tmp_path / "large.txt"
    large_file.write_text("F" * 5000, encoding="utf-8")
    registry = create_coding_tool_registry()

    result = registry.run(
        "read_file",
        {
            "path": "large.txt",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is True
    assert result.output_truncated is True
    assert result.result.startswith("F" * 100)
    assert "kept 4000 of 5000 chars" in result.result
    assert len(result.result) < 5000


def test_builtin_coding_tools_export_parameter_schemas():
    """测试内置 coding 工具都能导出参数 schema。"""
    registry = create_coding_tool_registry()

    schemas = {
        schema["name"]: schema
        for schema in registry.list_tool_schemas()
    }

    assert "path" in schemas["read_file"]["parameters"]["required"]
    assert "path" in schemas["write_file"]["parameters"]["required"]
    assert "content" in schemas["write_file"]["parameters"]["required"]
    assert "path" in schemas["edit_file"]["parameters"]["required"]
    assert "old_text" in schemas["edit_file"]["parameters"]["required"]
    assert "new_text" in schemas["edit_file"]["parameters"]["required"]
    assert "command" in schemas["run_command"]["parameters"]["required"]
    assert "workspace_root" in schemas["run_command"]["parameters"]["required"]
    assert "timeout_seconds" in schemas["run_command"]["parameters"]["required"]


def test_builtin_coding_tool_schemas_describe_selection_boundaries():
    """测试内置工具描述足够支持模型区分用途、边界和返回语义。"""
    registry = create_coding_tool_registry()

    schemas = {
        schema["name"]: schema
        for schema in registry.list_tool_schemas()
    }

    read_file = schemas["read_file"]
    assert "只读取" in read_file["description"]
    assert "不修改文件" in read_file["description"]
    assert "workspace_root" in read_file["description"]
    assert "返回文件文本" in read_file["description"]
    assert "相对路径" in read_file["parameters"]["properties"]["path"]["description"]

    write_file = schemas["write_file"]
    assert "新文本文件" in write_file["description"]
    assert "覆盖已有文件" in write_file["description"]
    assert "approval" in write_file["description"]
    assert "自动创建父目录" in write_file["description"]
    assert "workspace_root" in write_file["description"]
    assert "返回 ok" in write_file["description"]
    assert "完整文本内容" in write_file["parameters"]["properties"]["content"]["description"]

    edit_file = schemas["edit_file"]
    assert "局部编辑" in edit_file["description"]
    assert "只替换一次" in edit_file["description"]
    assert "old_text" in edit_file["description"]
    assert "出现多次" in edit_file["description"]
    assert "删除式编辑" in edit_file["description"]
    assert "approval" in edit_file["description"]
    assert "返回 ok" in edit_file["description"]
    assert "原文件中必须唯一出现" in edit_file["parameters"]["properties"]["old_text"]["description"]
    assert "替换后的文本" in edit_file["parameters"]["properties"]["new_text"]["description"]

    run_command = schemas["run_command"]
    assert "执行命令" in run_command["description"]
    assert "workspace_root" in run_command["description"]
    assert "timeout_seconds" in run_command["description"]
    for output_field in ("stdout", "stderr", "returncode", "timed_out"):
        assert output_field in run_command["description"]
    assert "list[str]" in run_command["parameters"]["properties"]["command"]["description"]
    assert "正数" in run_command["parameters"]["properties"]["timeout_seconds"]["description"]
    assert "默认使用 workspace_root" in run_command["parameters"]["properties"]["cwd"]["description"]
    assert "敏感" in run_command["parameters"]["properties"]["env"]["description"]
    assert "脱敏" in run_command["parameters"]["properties"]["env"]["description"]
