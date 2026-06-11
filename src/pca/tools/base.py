from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


JSON_TYPE_TO_PYTHON_TYPES: dict[str, tuple[type[Any], ...]] = {
    "string": (str,),
    "number": (int, float),
    "integer": (int,),
    "boolean": (bool,),
    "object": (dict,),
    "array": (list,),
}


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
