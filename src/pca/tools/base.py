from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


JSON_TYPE_TO_PYTHON_TYPES: dict[str, tuple[type[Any], ...]] = {
    "string": (str,),
    "number": (int, float),
    "integer": (int,),
    "boolean": (bool,),
    "object": (dict,),
    "array": (list,),
}

DEFAULT_MAX_OUTPUT_CHARS = 4000


class ToolErrorCode(Enum):
    """工具失败的稳定错误码，供 retry、audit 和 safety 测试复用。"""

    INVALID_ARGUMENT = "invalid_argument"
    UNKNOWN_TOOL = "unknown_tool"
    PERMISSION_DENIED = "permission_denied"
    PERMISSION_APPROVAL_REQUIRED = "permission_approval_required"
    RUNTIME_FAILED = "runtime_failed"
    CHECKPOINT_FAILED = "checkpoint_failed"
    ROLLBACK_FAILED = "rollback_failed"
    AUDIT_FAILED = "audit_failed"


def truncate_output(
    text: str,
    max_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
) -> tuple[str, bool]:
    """截断过长工具输出，并返回是否发生截断。"""
    # 修改前旧代码：无统一截断函数，工具输出会原样进入 ToolResult 和 message history。
    #
    # 问题：shell stdout/stderr 或文件内容过大时，会撑爆后续 LLM 上下文。
    if not isinstance(text, str):
        raise TypeError("output text must be a string")
    if not isinstance(max_chars, int) or isinstance(max_chars, bool):
        raise TypeError("max_chars must be an integer")
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")
    if len(text) <= max_chars:
        return text, False

    notice = f"\n[output truncated: kept {max_chars} of {len(text)} chars]"
    return text[:max_chars] + notice, True


@dataclass(frozen=True)
class ToolResult:
    """一次工具执行的结构化结果。"""

    # 修改前旧代码：
    # ok: bool
    # result: Any = None
    # error_type: str | None = None
    # error_message: str | None = None
    # duration_ms: int = 0
    #
    # 问题：结果信封只能表达成功/失败内容和耗时，无法把一次 Agent
    # 运行、一次工具调用、输出截断状态和稳定错误语义挂到同一个结果对象上。
    ok: bool
    result: Any = None
    error_type: str | None = None
    error_message: str | None = None
    error_code: ToolErrorCode | None = None
    duration_ms: int = 0
    trace_id: str | None = None
    tool_call_id: str | None = None
    output_truncated: bool = False

    def __post_init__(self) -> None:
        """校验结果信封自身，避免把含糊状态写回 Agent 轨迹。"""
        if not isinstance(self.ok, bool):
            raise TypeError("tool result ok must be a boolean")
        if not isinstance(self.duration_ms, int) or isinstance(self.duration_ms, bool):
            raise TypeError("tool result duration_ms must be an integer")
        if self.duration_ms < 0:
            raise ValueError("tool result duration_ms must be non-negative")
        if self.trace_id is not None and (
            not isinstance(self.trace_id, str) or self.trace_id.strip() == ""
        ):
            raise ValueError("tool result trace_id must be a non-empty string")
        if self.tool_call_id is not None and (
            not isinstance(self.tool_call_id, str) or self.tool_call_id.strip() == ""
        ):
            raise ValueError("tool result tool_call_id must be a non-empty string")
        if not isinstance(self.output_truncated, bool):
            raise TypeError("tool result output_truncated must be a boolean")
        if self.ok:
            if (
                self.error_type is not None
                or self.error_message is not None
                or self.error_code is not None
            ):
                raise ValueError("successful tool result cannot contain error fields")
        else:
            if not isinstance(self.error_type, str) or self.error_type.strip() == "":
                raise ValueError("failed tool result must contain error_type")
            if not isinstance(self.error_message, str):
                raise TypeError("failed tool result error_message must be a string")
            if self.error_code is None:
                object.__setattr__(self, "error_code", ToolErrorCode.RUNTIME_FAILED)
            if not isinstance(self.error_code, ToolErrorCode):
                raise TypeError("failed tool result error_code must be a ToolErrorCode")

    @classmethod
    def success(
        cls,
        result: Any,
        duration_ms: int,
        *,
        trace_id: str | None = None,
        tool_call_id: str | None = None,
        output_truncated: bool = False,
    ) -> "ToolResult":
        """构造成功结果。"""
        return cls(
            ok=True,
            result=result,
            duration_ms=duration_ms,
            trace_id=trace_id,
            tool_call_id=tool_call_id,
            output_truncated=output_truncated,
        )

    @classmethod
    def failure(
        cls,
        error_type: str,
        error_message: str,
        duration_ms: int,
        *,
        error_code: ToolErrorCode = ToolErrorCode.RUNTIME_FAILED,
        trace_id: str | None = None,
        tool_call_id: str | None = None,
        output_truncated: bool = False,
    ) -> "ToolResult":
        """构造失败结果。"""
        return cls(
            ok=False,
            result=None,
            error_type=error_type,
            error_message=error_message,
            error_code=error_code,
            duration_ms=duration_ms,
            trace_id=trace_id,
            tool_call_id=tool_call_id,
            output_truncated=output_truncated,
        )

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        duration_ms: int,
        *,
        trace_id: str | None = None,
        tool_call_id: str | None = None,
        output_truncated: bool = False,
    ) -> "ToolResult":
        """把异常转换成结构化失败结果。"""
        error_message = str(exc)
        return cls.failure(
            error_type=type(exc).__name__,
            error_message=error_message,
            error_code=classify_tool_exception(exc, error_message),
            duration_ms=duration_ms,
            trace_id=trace_id,
            tool_call_id=tool_call_id,
            output_truncated=output_truncated,
        )

    def __str__(self) -> str:
        """保持现有 message history 文本兼容，同时保留结构化字段。"""
        if self.ok:
            return str(self.result)
        return f"Tool execution failed: {self.error_type}: {self.error_message}"

    def __eq__(self, other: object) -> bool:
        """成功结果可与旧测试中的原始返回值比较。"""
        if isinstance(other, ToolResult):
            return (
                self.ok == other.ok
                and self.result == other.result
                and self.error_type == other.error_type
                and self.error_message == other.error_message
                and self.error_code == other.error_code
                and self.duration_ms == other.duration_ms
                and self.trace_id == other.trace_id
                and self.tool_call_id == other.tool_call_id
                and self.output_truncated == other.output_truncated
            )
        return self.ok and self.result == other

    def __getitem__(self, key: str) -> Any:
        """成功结果为 dict 时兼容 result["field"] 访问。"""
        if not self.ok:
            raise KeyError(key)
        if not isinstance(self.result, dict):
            raise TypeError("tool result payload is not subscriptable")
        return self.result[key]


def classify_tool_exception(
    exc: Exception,
    error_message: str | None = None,
) -> ToolErrorCode:
    """把当前工具链的异常映射为稳定错误码。"""
    message = str(exc) if error_message is None else error_message
    lowered_message = message.lower()

    # 修改前旧代码：审计持久化失败会落入普通 RUNTIME_FAILED。
    # 问题：调用方可能自动重试已经发生过副作用的工具。
    from pca.permissions.audit import AuditPersistenceError

    if isinstance(exc, AuditPersistenceError):
        return ToolErrorCode.AUDIT_FAILED
    checkpoint_failure_markers = (
        "checkpoint",
        "not a git repository",
        "git executable is not available",
        "git command failed",
    )

    if isinstance(exc, PermissionError):
        if "approval required" in lowered_message:
            return ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
        if "permission denied" in lowered_message:
            return ToolErrorCode.PERMISSION_DENIED
        return ToolErrorCode.PERMISSION_DENIED

    if isinstance(exc, KeyError):
        return ToolErrorCode.UNKNOWN_TOOL

    if isinstance(exc, (TypeError, ValueError)):
        if any(marker in lowered_message for marker in checkpoint_failure_markers):
            return ToolErrorCode.CHECKPOINT_FAILED
        return ToolErrorCode.INVALID_ARGUMENT

    if isinstance(exc, RuntimeError):
        if "rollback failed" in lowered_message:
            return ToolErrorCode.ROLLBACK_FAILED
        if any(marker in lowered_message for marker in checkpoint_failure_markers):
            return ToolErrorCode.CHECKPOINT_FAILED
        return ToolErrorCode.RUNTIME_FAILED

    return ToolErrorCode.RUNTIME_FAILED


@dataclass(frozen=True)
class ToolParameter:
    """工具参数 schema 中的一个字段。"""

    name: str
    type: str | tuple[str, ...]
    description: str
    required: bool = True

    def __post_init__(self) -> None:
        """校验参数 schema 自身，避免把错误 schema 暴露给 LLM。"""
        if not isinstance(self.name, str) or self.name.strip() == "":
            raise ValueError("tool parameter name must be a non-empty string")
        if isinstance(self.type, str):
            types = (self.type,)
        elif isinstance(self.type, tuple):
            types = self.type
        else:
            raise TypeError("tool parameter type must be a string or tuple of strings")

        if not types or any(
            not isinstance(type_name, str) or type_name not in JSON_TYPE_TO_PYTHON_TYPES
            for type_name in types
        ):
            raise ValueError("tool parameter type must be a supported JSON type")
        if not isinstance(self.description, str) or self.description.strip() == "":
            raise ValueError("tool parameter description must be a non-empty string")
        if not isinstance(self.required, bool):
            raise TypeError("tool parameter required must be a boolean")

    @property
    def types(self) -> tuple[str, ...]:
        """返回统一 tuple 形式的 JSON 类型列表。"""
        if isinstance(self.type, str):
            return (self.type,)
        return self.type

    def to_schema(self) -> dict[str, Any]:
        """导出单个参数的 JSON Schema 片段。"""
        if len(self.types) == 1:
            type_schema: str | list[str] = self.types[0]
        else:
            type_schema = list(self.types)
        return {
            "type": type_schema,
            "description": self.description,
        }

    def validate(self, arguments: dict[str, Any]) -> None:
        """校验一次工具调用是否满足当前参数声明。"""
        if self.name not in arguments:
            if self.required:
                raise ValueError(f"Missing required argument: {self.name}")
            return

        value = arguments[self.name]
        if value is None:
            if self.required:
                raise ValueError(f"Missing required argument: {self.name}")
            return

        allowed_types: tuple[type[Any], ...] = ()
        for type_name in self.types:
            allowed_types += JSON_TYPE_TO_PYTHON_TYPES[type_name]

        if isinstance(value, bool) and "boolean" not in self.types:
            expected = " or ".join(self.types)
            raise TypeError(f"argument {self.name} must be {expected}")
        if not isinstance(value, allowed_types):
            expected = " or ".join(self.types)
            raise TypeError(f"argument {self.name} must be {expected}")


@dataclass
class Tool:
    """Agent 可以调用的一个具体工具。"""

    name: str
    description: str
    handler: Callable[[dict[str, Any]], Any]
    parameters: tuple[ToolParameter, ...] = field(default_factory=tuple)

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
        if not isinstance(self.parameters, tuple):
            raise TypeError("tool parameters must be a tuple")
        if any(not isinstance(parameter, ToolParameter) for parameter in self.parameters):
            raise TypeError("tool parameters must contain ToolParameter instances")

    def run(self, arguments: dict[str, Any]) -> Any:
        """使用统一入口执行工具，避免 AgentLoop 直接依赖具体函数。"""
        # 修改前旧代码：
        # return self.handler(arguments)
        #
        # 问题：非 dict 参数会直接传给 handler，各工具的错误语义不一致。
        if not isinstance(arguments, dict):
            raise TypeError("tool arguments must be a dictionary")
        for parameter in self.parameters:
            parameter.validate(arguments)
        return self.handler(arguments)

    def to_schema(self) -> dict[str, Any]:
        """导出工具 schema，供后续真实 LLM adapter 或文档使用。"""
        properties = {
            parameter.name: parameter.to_schema()
            for parameter in self.parameters
        }
        required = [
            parameter.name
            for parameter in self.parameters
            if parameter.required
        ]
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": True,
            },
        }
