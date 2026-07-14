"""测试 Week 6 Day 3 的最小 retry policy。"""

from pca.tools import ToolErrorCode, ToolResult
from pca.tools.retry import RetryDecision, RetryPolicy, should_retry


def test_retry_policy_does_not_retry_successful_result() -> None:
    """测试成功工具结果不进入 retry 语义。"""
    result = ToolResult.success(result="ok", duration_ms=1)

    decision = RetryPolicy().decide(result)

    assert decision == RetryDecision(
        retryable=False,
        reason="successful result does not need retry",
    )
    assert should_retry(result) is False


def test_retry_policy_retries_runtime_failed_candidate() -> None:
    """测试普通 runtime 失败是可重试候选，但不代表自动重复执行。"""
    result = ToolResult.failure(
        error_type="RuntimeError",
        error_message="temporary process failure",
        error_code=ToolErrorCode.RUNTIME_FAILED,
        duration_ms=1,
    )

    decision = RetryPolicy().decide(result)

    assert decision.retryable is True
    assert decision.reason == "runtime failure may be transient"
    assert should_retry(result) is True


def test_retry_policy_does_not_retry_checkpoint_failure_by_default() -> None:
    """测试 checkpoint 失败默认不可重试，避免在保护层不可靠时继续副作用。"""
    result = ToolResult.failure(
        error_type="RuntimeError",
        error_message="git executable is not available",
        error_code=ToolErrorCode.CHECKPOINT_FAILED,
        duration_ms=1,
    )

    decision = RetryPolicy().decide(result)

    assert decision == RetryDecision(
        retryable=False,
        reason="checkpoint failure means recovery protection is unavailable",
    )


def test_retry_policy_never_retries_permission_or_argument_failures() -> None:
    """测试权限、审批、参数和未知工具错误都不是 retry 能解决的问题。"""
    non_retryable_codes = (
        ToolErrorCode.PERMISSION_DENIED,
        ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
        ToolErrorCode.INVALID_ARGUMENT,
        ToolErrorCode.UNKNOWN_TOOL,
        ToolErrorCode.AUDIT_FAILED,
    )

    for error_code in non_retryable_codes:
        result = ToolResult.failure(
            error_type="ValueError",
            error_message=error_code.value,
            error_code=error_code,
            duration_ms=1,
        )

        decision = RetryPolicy().decide(result)

        assert decision.retryable is False
        assert error_code.value in decision.reason


def test_retry_policy_never_retries_rollback_failed() -> None:
    """测试 rollback 失败必须 fail-closed，不能再次扩大副作用。"""
    result = ToolResult.failure(
        error_type="RuntimeError",
        error_message="file change failed and rollback failed",
        error_code=ToolErrorCode.ROLLBACK_FAILED,
        duration_ms=1,
    )

    decision = RetryPolicy().decide(result)

    assert decision == RetryDecision(
        retryable=False,
        reason="rollback failure must fail closed",
    )


def test_retry_policy_rejects_non_tool_result() -> None:
    """测试 retry policy 只消费 ToolResult，避免调用方传入含糊对象。"""
    policy = RetryPolicy()

    try:
        policy.decide("not-a-tool-result")  # type: ignore[arg-type]
    except TypeError as exc:
        assert "ToolResult" in str(exc)
    else:
        raise AssertionError("RetryPolicy.decide should reject non-ToolResult input")
