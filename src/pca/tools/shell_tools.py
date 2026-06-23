from typing import Any

from pca.permissions.policy import DecisionAction, PermissionPolicy
from pca.permissions.risk import classify_command
from pca.runtime.shell_runtime import ShellRuntime
from pca.tools.base import Tool, ToolParameter


class ShellCommandTool(Tool):
    """把 Agent 的 run_command 工具调用转发给 shell runtime。"""

    def __init__(
        self,
        runtime: ShellRuntime | None = None,
        permission_policy: PermissionPolicy | None = None,
    ) -> None:
        self._runtime = runtime or ShellRuntime()
        self._permission_policy = permission_policy or PermissionPolicy()
        super().__init__(
            name="run_command",
            description=(
                "执行前先经过 permission gate，再在 workspace_root 边界内执行命令，必须设置 timeout_seconds；"
                "返回 stdout、stderr、returncode 和 timed_out。"
            ),
            handler=self._run,
            parameters=(
                ToolParameter(
                    name="command",
                    type=("string", "array"),
                    description="要执行的命令；推荐使用 list[str]，字符串命令仅用于兼容简单 shell 场景",
                ),
                ToolParameter(
                    name="workspace_root",
                    type="string",
                    description="授权工作区根目录；命令和 cwd 都必须限制在此目录内",
                ),
                ToolParameter(
                    name="timeout_seconds",
                    type=("number", "string"),
                    description="命令超时时间，单位秒；必须是正数",
                ),
                ToolParameter(
                    name="cwd",
                    type="string",
                    description="命令工作目录；默认使用 workspace_root",
                    required=False,
                ),
                ToolParameter(
                    name="env",
                    type="object",
                    description="附加环境变量；会合并到当前进程环境中，敏感变量值会在返回输出中脱敏",
                    required=False,
                ),
            ),
        )

    def _run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """在进入真实 shell runtime 前执行权限 gate。"""
        # 修改前旧代码：
        # handler=self._runtime.run
        #
        # 问题：run_command 会直接进入 ShellRuntime，风险分类、策略判断和审批对象
        # 已经存在但没有接入执行前边界，危险命令仍可能被真实执行。
        assessment = classify_command(arguments["command"])
        decision = self._permission_policy.decide(assessment)

        if decision.action is DecisionAction.DENY:
            raise PermissionError(
                "Permission denied before shell execution: "
                f"action={decision.action.value}; "
                f"risk={assessment.level.value}; "
                f"rule={assessment.matched_rule}; "
                f"reason={decision.reason} {assessment.reason}"
            )

        if decision.action is DecisionAction.ASK:
            raise PermissionError(
                "Permission approval required before shell execution: "
                f"action={decision.action.value}; "
                f"risk={assessment.level.value}; "
                f"rule={assessment.matched_rule}; "
                f"reason={decision.reason} {assessment.reason}"
            )

        return self._runtime.run(arguments)


# 向后兼容的函数形式
def run_command(arguments: dict[str, Any]) -> dict[str, Any]:
    """向后兼容的函数形式：经过 shell gate 后执行命令并返回结构化结果。"""
    # 修改前旧代码：
    # return runtime_run_command(arguments)
    #
    # 问题：函数形式会绕过 ShellCommandTool 的权限 gate，导致同一个 run_command
    # 名称在工具注册表和直接调用时安全语义不一致。
    return ShellCommandTool().run(arguments)
