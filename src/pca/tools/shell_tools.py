from pathlib import Path
from typing import Any

from pca.permissions.audit import (
    AuditPersistenceError,
    ToolExecutionPhase,
    new_operation_id,
    record_permission_decision,
    record_tool_execution_event,
)
from pca.permissions.policy import DecisionAction, PermissionPolicy
from pca.permissions.risk import classify_command
from pca.runtime.interface import CommandRuntime
from pca.runtime.shell_runtime import ShellRuntime
from pca.tools.base import Tool, ToolParameter


class ShellCommandTool(Tool):
    """把 Agent 的 run_command 工具调用转发给 shell runtime。"""

    def __init__(
        self,
        runtime: CommandRuntime | None = None,
        permission_policy: PermissionPolicy | None = None,
        audit_path: Path | None = None,
    ) -> None:
        # 修改前旧代码：
        # runtime: ShellRuntime | None = None
        #
        # 问题：调用方类型边界写死到本地 ShellRuntime，虽然测试里已能注入 fake
        # runtime，但接口层没有显式表达“只依赖 run(arguments)”这个契约。
        self._runtime = runtime or ShellRuntime()
        self._permission_policy = permission_policy or PermissionPolicy()
        self._audit_path = audit_path
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
        audit_path = self._resolve_audit_path(arguments)
        operation_id = new_operation_id()

        # 审计在副作用前记录。ALLOW 写入失败必须阻止 runtime；ASK/DENY 本来
        # 就不会执行，因此保留原始 permission 结果，避免把审批语义改成存储错误。
        try:
            record_permission_decision(
                audit_path,
                operation_id=operation_id,
                tool_name=self.name,
                decision=decision,
                authorized=decision.action is DecisionAction.ALLOW,
            )
        except OSError as audit_error:
            if decision.action is DecisionAction.ALLOW:
                raise AuditPersistenceError(
                    phase="permission_decision",
                    side_effect_state="not_started",
                ) from audit_error

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

        # 修改前旧代码：
        # return self._runtime.run(arguments)
        #
        # 问题：permission allow 之后没有 started/succeeded/failed 事实，
        # executed=true 会被误读为命令已经成功完成。
        try:
            record_tool_execution_event(
                audit_path,
                operation_id=operation_id,
                tool_name=self.name,
                phase=ToolExecutionPhase.STARTED,
            )
        except OSError as audit_error:
            raise AuditPersistenceError(
                phase=ToolExecutionPhase.STARTED,
                side_effect_state="not_started",
            ) from audit_error

        try:
            result = self._runtime.run(arguments)
        except Exception as runtime_error:
            try:
                record_tool_execution_event(
                    audit_path,
                    operation_id=operation_id,
                    tool_name=self.name,
                    phase=ToolExecutionPhase.FAILED,
                )
            except OSError as audit_error:
                raise AuditPersistenceError(
                    phase=ToolExecutionPhase.FAILED,
                    side_effect_state="unknown",
                ) from runtime_error
            raise

        try:
            record_tool_execution_event(
                audit_path,
                operation_id=operation_id,
                tool_name=self.name,
                phase=ToolExecutionPhase.SUCCEEDED,
            )
        except OSError as audit_error:
            raise AuditPersistenceError(
                phase=ToolExecutionPhase.SUCCEEDED,
                side_effect_state="completed",
            ) from audit_error
        return result

    def _resolve_audit_path(self, arguments: dict[str, Any]) -> Path:
        """返回当前调用的审计文件；测试可注入临时路径隔离写入。"""
        if self._audit_path is not None:
            return self._audit_path
        # 不能从尚未通过 runtime 校验的 workspace_root 派生路径，否则 audit 会
        # 抢先创建不存在的工作区，或在只读工作区改变原有参数错误语义。
        return Path.cwd() / ".pca" / "permission-audit.jsonl"


# 向后兼容的函数形式
def run_command(arguments: dict[str, Any]) -> dict[str, Any]:
    """向后兼容的函数形式：经过 shell gate 后执行命令并返回结构化结果。"""
    # 修改前旧代码：
    # return runtime_run_command(arguments)
    #
    # 问题：函数形式会绕过 ShellCommandTool 的权限 gate，导致同一个 run_command
    # 名称在工具注册表和直接调用时安全语义不一致。
    return ShellCommandTool().run(arguments)
