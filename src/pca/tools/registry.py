
from dataclasses import dataclass , field
from typing import Any

from pca.tools.base import Tool


@dataclass
class ToolRegistry:

    _tools : dict[str,Tool] = field(default_factory=dict)

    def register(self,tool : Tool) -> None:
        if tool.name in self._tools:
            raise KeyError(f"Duplicate tool: {tool.name}")
        self._tools.update({tool.name:tool})

    def get(self,name:str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def run(self,name:str, arguments:dict[str,Any]) -> Any:
        tool = self.get(name)  # 这里会抛出 KeyError 如果工具不存在
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
