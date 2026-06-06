from dataclasses import dataclass, field
from typing import Any

from pca.tools.base import Tool


@dataclass
class ToolRegistry:
    """负责注册、查找和执行工具的统一入口。"""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        """注册一个工具；同名工具会让调用路由变得不确定，因此直接报错。"""
        # 修改前旧代码：
        # if tool.name in self._tools:
        #     raise KeyError(f"Duplicate tool: {tool.name}")
        # self._tools[tool.name] = tool
        #
        # 问题：非 Tool 对象会触发 AttributeError，而不是清晰的 TypeError。
        if not isinstance(tool, Tool):
            raise TypeError("ToolRegistry can only register Tool instances")
        if tool.name in self._tools:
            raise KeyError(f"Duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """按名称获取工具；不存在时用 KeyError 暴露调用链问题。"""
        # 修改前旧代码：
        # if name not in self._tools:
        #     raise KeyError(f"Unknown tool: {name}")
        #
        # 问题：空工具名和非字符串工具名没有被提前拒绝。
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("tool name must be a non-empty string")
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def run(self, name: str, arguments: dict[str, Any]) -> Any:
        """查找工具并执行，是 AgentLoop 面向工具系统的唯一入口。"""
        # 修改前旧代码：
        # tool = self.get(name)
        # return tool.run(arguments)
        #
        # 问题：arguments 不是 dict 时会一路传到具体工具，错误位置不清晰。
        if not isinstance(arguments, dict):
            raise TypeError("tool arguments must be a dictionary")
        tool = self.get(name)
        return tool.run(arguments)

    def exists(self, name: str) -> bool:
        if not isinstance(name, str) or name.strip() == "":
            return False
        return name in self._tools

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def unregister(self, name: str) -> None:
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("tool name must be a non-empty string")
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        del self._tools[name]

    def clear(self) -> None:
        self._tools.clear()
