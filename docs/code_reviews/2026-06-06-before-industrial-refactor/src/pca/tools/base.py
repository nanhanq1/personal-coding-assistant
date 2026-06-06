from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    """Agent 可以调用的一个具体工具。"""

    name: str
    description: str
    handler: Callable[[dict[str, Any]], Any]

    def run(self, arguments: dict[str, Any]) -> Any:
        """使用统一入口执行工具，避免 AgentLoop 直接依赖具体函数。"""
        return self.handler(arguments)
