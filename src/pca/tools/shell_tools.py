from typing import Any

from pca.runtime.shell_runtime import ShellRuntime, run_command as runtime_run_command
from pca.tools.base import Tool, ToolParameter


class ShellCommandTool(Tool):
    """把 Agent 的 run_command 工具调用转发给 shell runtime。"""

    def __init__(self, runtime: ShellRuntime | None = None) -> None:
        self._runtime = runtime or ShellRuntime()
        super().__init__(
            name="run_command",
            description="执行 shell 命令并返回结果。支持工作目录、超时和工作区边界检查。",
            handler=self._runtime.run,
            parameters=(
                ToolParameter(
                    name="command",
                    type=("string", "array"),
                    description="要执行的命令；推荐使用字符串列表形式",
                ),
                ToolParameter(name="workspace_root", type="string", description="授权工作区根目录"),
                ToolParameter(
                    name="timeout_seconds",
                    type=("number", "string"),
                    description="命令超时时间，单位秒",
                ),
                ToolParameter(name="cwd", type="string", description="工作目录", required=False),
                ToolParameter(name="env", type="object", description="附加环境变量", required=False),
            ),
        )


# 向后兼容的函数形式
def run_command(arguments: dict[str, Any]) -> dict[str, Any]:
    """向后兼容的函数形式：执行 shell 命令并返回结构化结果。"""
    return runtime_run_command(arguments)
