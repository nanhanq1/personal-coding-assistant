from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from pca.tools.base import Tool, ToolResult, truncate_output


TRUNCATABLE_DICT_FIELDS = ("stdout", "stderr")


@dataclass
class ToolRegistry:
    """负责注册、查找和执行工具的统一入口。"""

    _tools: dict[str, Tool] = field(default_factory=dict)
    _stats: dict[str, dict[str, int]] = field(default_factory=dict)

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

    def run(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        """查找工具并执行，是 AgentLoop 面向工具系统的唯一入口。"""
        # 修改前旧代码：
        # tool = self.get(name)
        # return tool.run(arguments)
        #
        # 问题：arguments 不是 dict 时会一路传到具体工具，错误位置不清晰。
        started_at = perf_counter()
        try:
            if not isinstance(arguments, dict):
                raise TypeError("tool arguments must be a dictionary")
            tool = self.get(name)
            result = tool.run(arguments)
        except Exception as exc:
            duration_ms = int((perf_counter() - started_at) * 1000)
            failure = ToolResult.from_exception(exc, duration_ms=duration_ms)
            self._record_stats(name=name, ok=False, duration_ms=duration_ms)
            return failure
        # 修改前旧代码：
        # return ToolResult.success(result=result, duration_ms=duration_ms)
        #
        # 问题：工具输出会原样进入 ToolResult，shell/file 大输出可能撑爆 message history。
        result, output_truncated = _truncate_tool_result_payload(result)
        duration_ms = int((perf_counter() - started_at) * 1000)
        self._record_stats(name=name, ok=True, duration_ms=duration_ms)
        return ToolResult.success(
            result=result,
            duration_ms=duration_ms,
            output_truncated=output_truncated,
        )

    def get_stats(self) -> dict[str, dict[str, int]]:
        """返回工具调用统计快照，避免调用方修改注册表内部状态。"""
        return {
            tool_name: stats.copy()
            for tool_name, stats in self._stats.items()
        }

    def _record_stats(self, name: str, ok: bool, duration_ms: int) -> None:
        """在 ToolRegistry 统一入口记录工具调用结果。"""
        # 修改前旧代码：
        # ToolRegistry.run(...) 只返回 ToolResult，不记录任何调用统计。
        #
        # 问题：上层无法知道每个工具被调用了多少次、失败了多少次。
        stats = self._stats.setdefault(
            name,
            {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_duration_ms": 0,
            },
        )
        stats["calls"] += 1
        if ok:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        stats["total_duration_ms"] += duration_ms

    def exists(self, name: str) -> bool:
        if not isinstance(name, str) or name.strip() == "":
            return False
        return name in self._tools

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def list_tool_schemas(self) -> list[dict[str, Any]]:
        """导出所有已注册工具的 schema，供 LLM adapter 构造 tool 列表。"""
        return [
            tool.to_schema()
            for tool in self._tools.values()
        ]

    def unregister(self, name: str) -> None:
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("tool name must be a non-empty string")
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        del self._tools[name]

    def clear(self) -> None:
        self._tools.clear()
        self._stats.clear()


def _truncate_tool_result_payload(result: Any) -> tuple[Any, bool]:
    """在结构化结果边界截断可进入 message history 的文本输出。"""
    if isinstance(result, str):
        return truncate_output(result)
    if isinstance(result, dict):
        truncated_payload = result.copy()
        output_truncated = False
        for field in TRUNCATABLE_DICT_FIELDS:
            value = truncated_payload.get(field)
            if isinstance(value, str):
                truncated_text, was_truncated = truncate_output(value)
                truncated_payload[field] = truncated_text
                output_truncated = output_truncated or was_truncated
        if output_truncated:
            return truncated_payload, True
    return result, False
