"""文件检查点与回滚。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pca.runtime.workspace import PathInput, Workspace


@dataclass(frozen=True)
class _FileSnapshot:
    path: Path
    existed: bool
    content: bytes | None = None


@dataclass(frozen=True)
class FileCheckpoint:
    """保存一组 workspace 内文件在某个时刻的状态。"""

    workspace: Workspace
    snapshots: tuple[_FileSnapshot, ...]

    @classmethod
    def create(cls, workspace: Workspace, paths: Iterable[PathInput]) -> "FileCheckpoint":
        """为显式传入的文件路径创建快照。"""
        if not isinstance(workspace, Workspace):
            raise TypeError("workspace must be a Workspace")

        snapshots: list[_FileSnapshot] = []
        for path in paths:
            resolved_path = workspace.resolve_path(path)
            snapshots.append(cls._snapshot_file(resolved_path))
        return cls(workspace=workspace, snapshots=tuple(snapshots))

    def restore(self) -> None:
        """把被跟踪文件恢复到快照时的状态。"""
        for snapshot in self.snapshots:
            if snapshot.existed:
                self._restore_existing_file(snapshot)
            else:
                self._restore_missing_file(snapshot)

    @staticmethod
    def _snapshot_file(path: Path) -> _FileSnapshot:
        # 修改前旧代码：
        # """检查点与回滚占位模块，计划在第 7 周实现。"""
        #
        # 问题：checkpoint 不能再停留在占位状态；Day 2 需要能记录文件是否存在和原始 bytes。
        if not path.exists():
            return _FileSnapshot(path=path, existed=False)
        if path.is_dir():
            raise ValueError(f"checkpoint path must be a file, not a directory: {path}")
        return _FileSnapshot(path=path, existed=True, content=path.read_bytes())

    @staticmethod
    def _restore_existing_file(snapshot: _FileSnapshot) -> None:
        if snapshot.path.exists() and snapshot.path.is_dir():
            raise IsADirectoryError(snapshot.path)
        snapshot.path.parent.mkdir(parents=True, exist_ok=True)
        snapshot.path.write_bytes(snapshot.content or b"")

    @staticmethod
    def _restore_missing_file(snapshot: _FileSnapshot) -> None:
        if not snapshot.path.exists():
            return
        if snapshot.path.is_dir():
            raise IsADirectoryError(snapshot.path)
        snapshot.path.unlink()


@dataclass(frozen=True)
class GitCheckpoint:
    """保存 git workspace 中 tracked working tree 的 diff 快照。"""

    workspace: Workspace
    diff: str

    @classmethod
    def create(cls, workspace: Workspace) -> "GitCheckpoint":
        """保存当前 tracked working tree 相对 index 的 diff。"""
        # 修改前旧代码：
        # """文件检查点与回滚。"""
        #
        # 问题：Day 2 的 FileCheckpoint 只能处理显式文件列表；
        # Day 3 需要一个面向 git repo dirty tree 的 diff checkpoint。
        if not isinstance(workspace, Workspace):
            raise TypeError("workspace must be a Workspace")

        _ensure_git_workspace(workspace)
        diff = _run_git(workspace, ["diff", "--binary", "--", "."])
        return cls(workspace=workspace, diff=diff)

    def restore(self) -> None:
        """恢复 tracked working tree 到 checkpoint 创建时的 dirty 状态。"""
        _ensure_git_workspace(self.workspace)
        _run_git(self.workspace, ["restore", "--worktree", "--", "."])
        if self.diff:
            _run_git(self.workspace, ["apply", "--whitespace=nowarn", "-"], input_text=self.diff)


def _ensure_git_workspace(workspace: Workspace) -> None:
    result = _run_git_raw(workspace, ["rev-parse", "--is-inside-work-tree"])
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise ValueError(f"workspace is not a git repository: {workspace.root}")


def _run_git(workspace: Workspace, args: list[str], *, input_text: str | None = None) -> str:
    result = _run_git_raw(workspace, args, input_text=input_text)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise RuntimeError(detail)
    return result.stdout


def _run_git_raw(
    workspace: Workspace,
    args: list[str],
    *,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=workspace.root,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable is not available") from exc
