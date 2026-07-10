"""工具失败后的最小 retry policy。"""

from dataclasses import dataclass

from pca.tools.base import ToolErrorCode, ToolResult


NON_RETRYABLE_ERROR_REASONS: dict[ToolErrorCode, str] = {
    ToolErrorCode.INVALID_ARGUMENT: "invalid_argument is not retryable",
    ToolErrorCode.UNKNOWN_TOOL: "unknown_tool is not retryable",
    ToolErrorCode.PERMISSION_DENIED: "permission_denied is not retryable",
    ToolErrorCode.PERMISSION_APPROVAL_REQUIRED: (
        "permission_approval_required is not retryable"
    ),
    ToolErrorCode.CHECKPOINT_FAILED: (
        "checkpoint failure means recovery protection is unavailable"
    ),
    ToolErrorCode.ROLLBACK_FAILED: "rollback failure must fail closed",
}


@dataclass(frozen=True)
class RetryDecision:
    """一次工具失败是否允许 retry 的策略判断结果。"""

    retryable: bool
    reason: str

    def __post_init__(self) -> None:
        """校验 retry 决策自身，避免出现没有解释的策略结果。"""
        if not isinstance(self.retryable, bool):
            raise TypeError("retryable must be a boolean")
        if not isinstance(self.reason, str) or self.reason.strip() == "":
            raise ValueError("retry reason must be a non-empty string")


@dataclass(frozen=True)
class RetryPolicy:
    """基于 ToolResult.error_code 的最小重试策略。"""

    def decide(self, result: ToolResult) -> RetryDecision:
        """判断一次工具结果是否只是可重试候选，不负责重新执行工具。"""
        # 修改前旧代码：无 retry policy；调用方只能读 error_type/error_message
        # 或依赖自然语言判断下一步。
        #
        # 问题：permission、参数、rollback 等失败如果被误当成可重试，会重复
        # 危险副作用；runtime 临时失败又需要一个稳定的策略入口。
        if not isinstance(result, ToolResult):
            raise TypeError("RetryPolicy.decide expects a ToolResult")

        if result.ok:
            return RetryDecision(
                retryable=False,
                reason="successful result does not need retry",
            )

        error_code = result.error_code
        if error_code is ToolErrorCode.RUNTIME_FAILED:
            return RetryDecision(
                retryable=True,
                reason="runtime failure may be transient",
            )

        if error_code in NON_RETRYABLE_ERROR_REASONS:
            return RetryDecision(
                retryable=False,
                reason=NON_RETRYABLE_ERROR_REASONS[error_code],
            )

        return RetryDecision(
            retryable=False,
            reason="missing error code is not retryable",
        )


def should_retry(result: ToolResult, policy: RetryPolicy | None = None) -> bool:
    """返回布尔 retry 判断；适合调用方只需要简单分支时使用。"""
    active_policy = policy or RetryPolicy()
    return active_policy.decide(result).retryable
