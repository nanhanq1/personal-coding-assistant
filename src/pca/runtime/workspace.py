"""Workspace 边界抽象。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PathInput = str | os.PathLike[str]


@dataclass(frozen=True)
class Workspace:
    """表示一个已授权的本地工作区根目录。"""

    root: PathInput

    def __post_init__(self) -> None:
        # 修改前旧代码：
        # """工作区抽象占位模块，计划在第 7 周实现。"""
        #
        # 问题：文件工具和 shell runtime 已经各自维护路径边界，
        # 但 runtime 层没有统一 Workspace(root) 对象可供 checkpoint/rollback 复用。
        resolved_root = self._resolve_root(self.root)
        object.__setattr__(self, "root", resolved_root)

    def resolve_path(self, path: PathInput) -> Path:
        """把输入路径解析为 workspace 内的绝对路径。"""
        raw_path = self._coerce_path(path, label="path")
        if raw_path.is_absolute():
            resolved_path = raw_path.resolve()
        else:
            resolved_path = (self.root / raw_path).resolve()

        if not self._is_inside(resolved_path):
            raise ValueError(f"path is outside workspace: {path}")
        return resolved_path

    def contains(self, path: PathInput) -> bool:
        """判断路径解析后是否位于 workspace 内。"""
        try:
            self.resolve_path(path)
        except (OSError, TypeError, ValueError):
            return False
        return True

    @classmethod
    def _resolve_root(cls, root: PathInput) -> Path:
        raw_root = cls._coerce_path(root, label="workspace root")
        resolved_root = raw_root.resolve()
        if not resolved_root.exists() or not resolved_root.is_dir():
            raise ValueError(f"workspace root must be an existing directory: {root}")
        return resolved_root

    @staticmethod
    def _coerce_path(value: PathInput, *, label: str) -> Path:
        if not isinstance(value, (str, os.PathLike)):
            raise TypeError(f"{label} must be a string or path-like object")
        if isinstance(value, str) and value.strip() == "":
            raise ValueError(f"{label} must be a non-empty path")
        return Path(value)

    def _is_inside(self, path: Path) -> bool:
        return path == self.root or self.root in path.parents
