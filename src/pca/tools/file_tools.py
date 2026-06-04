from pathlib import Path
from typing import Any


def _resolve_workspace_path(arguments: dict[str, Any]) -> Path:
    """把工具参数中的路径解析为工作区内的绝对路径。"""
    raw_path = arguments["path"]
    if raw_path is None or str(raw_path).strip() == "":
        raise ValueError("path must be a non-empty string")

    workspace_root = Path(arguments.get("workspace_root", Path.cwd())).resolve()
    requested_path = Path(str(raw_path))

    if requested_path.is_absolute():
        resolved_path = requested_path.resolve()
    else:
        resolved_path = (workspace_root / requested_path).resolve()

    if resolved_path != workspace_root and workspace_root not in resolved_path.parents:
        raise ValueError(f"path is outside workspace: {raw_path}")

    return resolved_path


def read_file(arguments: dict[str, Any]) -> str:
    """读取工作区内的文件内容。"""
    path = _resolve_workspace_path(arguments)
    return path.read_text(encoding="utf-8")


def write_file(arguments: dict[str, Any]) -> str:
    """写入工作区内的文件内容。"""
    path = _resolve_workspace_path(arguments)
    content = arguments["content"]
    if content is None:
        raise ValueError("content must be a string")

    path.write_text(str(content), encoding="utf-8")
    return "ok"
