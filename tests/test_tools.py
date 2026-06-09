"""测试工具注册表功能"""
from typing import Any

import pytest
from pca.tools import create_coding_tool_registry
from pca.tools.base import Tool, ToolParameter
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
    assert result == "hello"

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


def test_run_nonexistent_tool_raises_keyerror():
    """测试执行不存在的工具会报 KeyError"""
    registry = ToolRegistry()

    # 执行不存在的工具应该抛出 KeyError
    with pytest.raises(KeyError, match="Unknown tool: nonexistent"):
        registry.run("nonexistent", {})


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
    assert "command" in schemas["run_command"]["parameters"]["required"]
    assert "workspace_root" in schemas["run_command"]["parameters"]["required"]
    assert "timeout_seconds" in schemas["run_command"]["parameters"]["required"]
