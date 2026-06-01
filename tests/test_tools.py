"""测试工具注册表功能"""
from typing import Any

import pytest
from pca.tools.base import Tool
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
    assert registry.exists("echo") == True
    assert registry.exists("nonexistent") == False

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
    assert registry.exists("test") == True

    # 注销工具
    registry.unregister("test")

    # 注销后应该不存在
    assert registry.exists("test") == False

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
