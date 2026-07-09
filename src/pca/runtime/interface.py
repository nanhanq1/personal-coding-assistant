"""命令 runtime 的最小接口。"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CommandRuntime(Protocol):
    """执行命令的结构化接口，隐藏本地 shell、fake 或未来 sandbox 实现。"""

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """执行命令并返回 stdout、stderr、returncode、timed_out 等结构化结果。"""
        ...
