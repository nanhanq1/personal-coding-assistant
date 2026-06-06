from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    """Agent 可以调用的一个具体工具。"""

    name: str
    description: str
    handler: Callable[[dict[str, Any]], Any]

    def __post_init__(self) -> None:
        """在注册前校验工具元数据，避免坏工具进入调用链。"""
        # 修改前旧代码：
        # @dataclass
        # class Tool:
        #     name: str
        #     description: str
        #     handler: Callable[[dict[str, Any]], Any]
        #
        # 问题：工具名、描述和 handler 不校验，坏工具会进入 ToolRegistry。
        if not isinstance(self.name, str) or self.name.strip() == "":
            raise ValueError("tool name must be a non-empty string")
        if not isinstance(self.description, str) or self.description.strip() == "":
            raise ValueError("tool description must be a non-empty string")
        if not callable(self.handler):
            raise TypeError("tool handler must be callable")

    def run(self, arguments: dict[str, Any]) -> Any:
        """使用统一入口执行工具，避免 AgentLoop 直接依赖具体函数。"""
        # 修改前旧代码：
        # return self.handler(arguments)
        #
        # 问题：非 dict 参数会直接传给 handler，各工具的错误语义不一致。
        if not isinstance(arguments, dict):
            raise TypeError("tool arguments must be a dictionary")
        return self.handler(arguments)
