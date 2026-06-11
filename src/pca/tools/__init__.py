"""工具抽象与内置 coding 工具模块包。"""

from pca.tools.base import Tool, ToolParameter
from pca.tools.file_tools import EditFileTool, ReadFileTool, WriteFileTool
from pca.tools.registry import ToolRegistry
from pca.tools.shell_tools import ShellCommandTool


def create_coding_tool_registry() -> ToolRegistry:
    """创建内置 coding 工具注册表，供 AgentLoop 统一路由工具调用。"""
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    registry.register(ShellCommandTool())
    return registry


__all__ = [
    "EditFileTool",
    "ReadFileTool",
    "ShellCommandTool",
    "Tool",
    "ToolParameter",
    "ToolRegistry",
    "WriteFileTool",
    "create_coding_tool_registry",
]
