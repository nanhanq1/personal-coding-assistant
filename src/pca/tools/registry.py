from dataclasses import dataclass, field
from typing import Any

from pca.tools.base import Tool


@dataclass
class ToolRegistry:
    """负责注册、查找和执行工具的统一入口。"""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        """注册一个工具；同名工具会让调用路由变得不确定，因此直接报错。"""
        if tool.name in self._tools:
            raise KeyError(f"Duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """按名称获取工具；不存在时用 KeyError 暴露调用链问题。"""
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def run(self, name: str, arguments: dict[str, Any]) -> Any:
        """查找工具并执行，是 AgentLoop 面向工具系统的唯一入口。"""
        tool = self.get(name)
        return tool.run(arguments)

    def exists(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def unregister(self, name: str) -> None:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        del self._tools[name]

    def clear(self) -> None:
        self._tools.clear()
