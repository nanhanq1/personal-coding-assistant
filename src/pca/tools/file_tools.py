from pathlib import Path
from typing import Any, Callable

from pca.permissions.file_risk import classify_file_change
from pca.permissions.policy import DecisionAction, PermissionPolicy
from pca.runtime.checkpoints import FileCheckpoint
from pca.runtime.workspace import Workspace
from pca.tools.base import Tool, ToolParameter


DEFAULT_MAX_READ_FILE_BYTES = 1024 * 1024
BINARY_DETECTION_SAMPLE_BYTES = 1024


class ReadFileTool(Tool):
    """读取工作区内的文件内容。"""

    def __init__(self) -> None:
        super().__init__(
            name="read_file",
            description=(
                "读取工作区内的文件内容；只读取 workspace_root 内的小型文本文件内容，不修改文件；"
                "适合在编辑前查看真实文件状态，返回文件文本。"
            ),
            handler=self._run,
            parameters=(
                ToolParameter(
                    name="path",
                    type="string",
                    description="要读取的文件路径；相对路径会基于 workspace_root 解析",
                ),
                ToolParameter(
                    name="workspace_root",
                    type="string",
                    description="允许读取的工作区根目录；未提供时使用当前进程目录",
                    required=False,
                ),
            ),
        )

    def _run(self, arguments: dict[str, Any]) -> str:
        """读取工作区内的文件内容。"""
        path = _resolve_workspace_path(arguments)
        # 修改前旧代码：
        # if path.is_dir():
        #     raise IsADirectoryError(f"path is a directory: {path}")
        # return path.read_text(encoding="utf-8")
        #
        # 问题：只检查目录，不限制文件大小，也不拒绝明显二进制内容。
        if path.is_dir():
            raise IsADirectoryError(f"path is a directory: {path}")
        _ensure_readable_text_file(path)
        return path.read_text(encoding="utf-8")


class WriteFileTool(Tool):
    """写入工作区内的文件内容。"""

    def __init__(self, permission_policy: PermissionPolicy | None = None) -> None:
        self._permission_policy = permission_policy or PermissionPolicy()
        super().__init__(
            name="write_file",
            description=(
                "写入工作区内的文件内容；写入 workspace_root 内的新文本文件，必要时自动创建父目录；"
                "覆盖已有文件会触发 permission approval，不会静默写盘；成功时返回 ok。"
            ),
            handler=self._run,
            parameters=(
                ToolParameter(
                    name="path",
                    type="string",
                    description="要写入的文件路径；相对路径会基于 workspace_root 解析",
                ),
                ToolParameter(
                    name="content",
                    type="string",
                    description="要写入新文件的完整文本内容",
                ),
                ToolParameter(
                    name="workspace_root",
                    type="string",
                    description="允许写入的工作区根目录；未提供时使用当前进程目录",
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

        # 修改前旧代码：
        # path.parent.mkdir(parents=True, exist_ok=True)
        # path.write_text(content, encoding="utf-8")
        #
        # 问题：覆盖已有文件会静默写盘，没有进入 permission gate。
        _ensure_file_permission(
            tool_name=self.name,
            path=path,
            permission_policy=self._permission_policy,
        )

        # 修改前旧代码：
        # path.parent.mkdir(parents=True, exist_ok=True)
        # path.write_text(content, encoding="utf-8")
        #
        # 问题：permission 已允许后，如果写盘中途失败，半成品文件会留在 workspace 中。
        _run_with_file_checkpoint(
            workspace_root=_resolve_workspace_root(arguments),
            path=path,
            operation=lambda: _write_text_file(path, content),
        )
        return "ok"


class EditFileTool(Tool):
    """对工作区内已有文件执行一次精确局部替换。"""

    def __init__(self, permission_policy: PermissionPolicy | None = None) -> None:
        self._permission_policy = permission_policy or PermissionPolicy()
        super().__init__(
            name="edit_file",
            description=(
                "对工作区内已有文本文件做局部编辑；只替换一次在文件中唯一出现的 old_text；"
                "如果 old_text 不存在或出现多次会拒绝写入，删除式编辑会触发 permission approval；"
                "成功时返回 ok。"
            ),
            handler=self._run,
            parameters=(
                ToolParameter(
                    name="path",
                    type="string",
                    description="要编辑的文件路径；相对路径会基于 workspace_root 解析",
                ),
                ToolParameter(
                    name="old_text",
                    type="string",
                    description="原文件中必须唯一出现的待替换文本；不能为空",
                ),
                ToolParameter(
                    name="new_text",
                    type="string",
                    description="替换后的文本；空字符串会被视为删除式编辑并触发 approval",
                ),
                ToolParameter(
                    name="workspace_root",
                    type="string",
                    description="允许编辑的工作区根目录；未提供时使用当前进程目录",
                    required=False,
                ),
            ),
        )

    def _run(self, arguments: dict[str, Any]) -> str:
        """读取文件，确认 old_text 唯一出现，然后写回替换后的内容。"""
        path = _resolve_workspace_path(arguments)
        old_text = arguments.get("old_text")
        new_text = arguments.get("new_text")

        if path.is_dir():
            raise IsADirectoryError(f"path is a directory: {path}")
        if old_text is None:
            raise ValueError("old_text must be a non-empty string")
        if not isinstance(old_text, str):
            raise TypeError("old_text must be a string")
        if old_text == "":
            raise ValueError("old_text must be a non-empty string")
        if new_text is None:
            raise ValueError("new_text must be a string")
        if not isinstance(new_text, str):
            raise TypeError("new_text must be a string")

        # 修改前旧代码：
        # content = path.read_text(encoding="utf-8")
        # occurrences = content.count(old_text)
        # ...
        # path.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        #
        # 问题：删除式编辑会静默写盘，没有进入 permission gate。
        _ensure_file_permission(
            tool_name=self.name,
            path=path,
            permission_policy=self._permission_policy,
            old_text=old_text,
            new_text=new_text,
        )
        content = path.read_text(encoding="utf-8")
        occurrences = content.count(old_text)
        if occurrences == 0:
            raise ValueError("old_text was not found")
        if occurrences > 1:
            raise ValueError("old_text appears multiple times")

        # 修改前旧代码：
        # path.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        #
        # 问题：permission 已允许后，如果写盘阶段失败，文件可能停在替换后的半完成状态。
        _run_with_file_checkpoint(
            workspace_root=_resolve_workspace_root(arguments),
            path=path,
            operation=lambda: _write_text_file(
                path,
                content.replace(old_text, new_text, 1),
            ),
        )
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


def _ensure_readable_text_file(path: Path) -> None:
    """在读取前检查文件资源边界，避免大文件或二进制内容进入上下文。"""
    file_size = path.stat().st_size
    if file_size > DEFAULT_MAX_READ_FILE_BYTES:
        raise ValueError(
            "file is too large: "
            f"{path} ({file_size} bytes > {DEFAULT_MAX_READ_FILE_BYTES} bytes)"
        )

    with path.open("rb") as file:
        sample = file.read(BINARY_DETECTION_SAMPLE_BYTES)
    if b"\x00" in sample:
        raise ValueError(f"file appears to be binary: {path}")


def _ensure_file_permission(
    *,
    tool_name: str,
    path: Path,
    permission_policy: PermissionPolicy,
    old_text: str | None = None,
    new_text: str | None = None,
) -> None:
    """在文件写盘前执行最小 permission gate。"""
    assessment = classify_file_change(
        tool_name=tool_name,
        path=path,
        old_text=old_text,
        new_text=new_text,
    )
    decision = permission_policy.decide(assessment)

    if decision.action is DecisionAction.ALLOW:
        return

    if decision.action is DecisionAction.ASK:
        raise PermissionError(
            "Permission approval required before file change: "
            f"action={decision.action.value}; "
            f"risk={assessment.level.value}; "
            f"rule={assessment.matched_rule}; "
            f"reason={decision.reason} {assessment.reason}"
        )

    if decision.action is DecisionAction.DENY:
        raise PermissionError(
            "Permission denied before file change: "
            f"action={decision.action.value}; "
            f"risk={assessment.level.value}; "
            f"rule={assessment.matched_rule}; "
            f"reason={decision.reason} {assessment.reason}"
        )


def _run_with_file_checkpoint(
    *,
    workspace_root: Path,
    path: Path,
    operation: Callable[[], None],
) -> None:
    """在允许进入副作用路径后执行文件修改，失败时恢复本地文件状态。"""
    workspace = Workspace(workspace_root)
    checkpoint = FileCheckpoint.create(workspace, [path])
    try:
        operation()
    except Exception as operation_error:
        try:
            checkpoint.restore()
        except Exception as rollback_error:
            raise RuntimeError(
                "file change failed and rollback failed: "
                f"original={operation_error}; rollback={rollback_error}"
            ) from operation_error
        raise


def _write_text_file(path: Path, content: str) -> None:
    """写入文本文件；独立函数让 rollback 集成点保持清晰。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# 向后兼容的函数形式
def read_file(arguments: dict[str, Any]) -> str:
    """向后兼容的函数形式：读取工作区内的文件内容。"""
    tool = ReadFileTool()
    return tool.run(arguments)


def write_file(arguments: dict[str, Any]) -> str:
    """向后兼容的函数形式：写入工作区内的文件内容。"""
    tool = WriteFileTool()
    return tool.run(arguments)


def edit_file(arguments: dict[str, Any]) -> str:
    """向后兼容的函数形式：对工作区内文件执行一次精确局部替换。"""
    tool = EditFileTool()
    return tool.run(arguments)
