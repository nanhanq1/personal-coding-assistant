from pathlib import Path
from typing import Any

from pca.tools.base import Tool, ToolParameter


class ReadFileTool(Tool):
    """读取工作区内的文件内容。"""

    def __init__(self) -> None:
        super().__init__(
            name="read_file",
            description="读取工作区内的文件内容。参数：path (文件路径), workspace_root (工作区根目录)",
            handler=self._run,
            parameters=(
                ToolParameter(name="path", type="string", description="要读取的文件路径"),
                ToolParameter(
                    name="workspace_root",
                    type="string",
                    description="允许读取的工作区根目录",
                    required=False,
                ),
            ),
        )

    def _run(self, arguments: dict[str, Any]) -> str:
        """读取工作区内的文件内容。"""
        path = _resolve_workspace_path(arguments)
        # 修改前旧代码：
        # return path.read_text(encoding="utf-8")
        #
        # 问题：读取目录时依赖操作系统抛 PermissionError，错误语义不稳定。
        if path.is_dir():
            raise IsADirectoryError(f"path is a directory: {path}")
        return path.read_text(encoding="utf-8")


class WriteFileTool(Tool):
    """写入工作区内的文件内容。"""

    def __init__(self) -> None:
        super().__init__(
            name="write_file",
            description="写入工作区内的文件内容。参数：path (文件路径), content (内容), workspace_root (工作区根目录)",
            handler=self._run,
            parameters=(
                ToolParameter(name="path", type="string", description="要写入的文件路径"),
                ToolParameter(name="content", type="string", description="要写入的文本内容"),
                ToolParameter(
                    name="workspace_root",
                    type="string",
                    description="允许写入的工作区根目录",
                    required=False,
                ),
            ),
        )

    def _run(self, arguments: dict[str, Any]) -> str:
        """写入工作区内的文件内容。"""
        path = _resolve_workspace_path(arguments)
        content = arguments.get("content")

        # 修改前旧代码：
        # if content is None:
        #     raise ValueError("content must be a string")
        # path.write_text(str(content), encoding="utf-8")
        #
        # 问题：dict/list 会被静默 str(...) 成伪文件内容，掩盖 LLM 参数错误。
        if content is None:
            raise ValueError("content must be a string")
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return "ok"


def _resolve_workspace_path(arguments: dict[str, Any]) -> Path:
    """把工具参数中的路径解析为工作区内的绝对路径。"""
    raw_path = arguments.get("path")
    if raw_path is None:
        raise ValueError("path must be a non-empty string")
    if not isinstance(raw_path, str):
        raise TypeError("path must be a string")
    if raw_path.strip() == "":
        raise ValueError("path must be a non-empty string")

    # 修改前旧代码：
    # workspace_root = Path(arguments.get("workspace_root", Path.cwd())).resolve()
    #
    # 问题：workspace_root 不存在或是文件时也会继续拼路径，错误会延迟到读写阶段。
    workspace_root = _resolve_workspace_root(arguments)
    requested_path = Path(raw_path)

    if requested_path.is_absolute():
        resolved_path = requested_path.resolve()
    else:
        resolved_path = (workspace_root / requested_path).resolve()

    if resolved_path != workspace_root and workspace_root not in resolved_path.parents:
        raise ValueError(f"path is outside workspace: {raw_path}")

    return resolved_path


def _resolve_workspace_root(arguments: dict[str, Any]) -> Path:
    """解析并校验允许文件工具操作的工作区根目录。"""
    raw_workspace_root = arguments.get("workspace_root", Path.cwd())
    if raw_workspace_root is None or str(raw_workspace_root).strip() == "":
        raise ValueError("workspace_root must be a non-empty directory")

    workspace_root = Path(str(raw_workspace_root)).resolve()
    if not workspace_root.exists() or not workspace_root.is_dir():
        raise ValueError(f"workspace_root must be an existing directory: {raw_workspace_root}")
    return workspace_root


# 向后兼容的函数形式
def read_file(arguments: dict[str, Any]) -> str:
    """向后兼容的函数形式：读取工作区内的文件内容。"""
    tool = ReadFileTool()
    return tool.run(arguments)


def write_file(arguments: dict[str, Any]) -> str:
    """向后兼容的函数形式：写入工作区内的文件内容。"""
    tool = WriteFileTool()
    return tool.run(arguments)
