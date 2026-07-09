from pathlib import Path

import pytest

from pca.runtime.workspace import Workspace


class TestWorkspace:
    """测试 Workspace 抽象的根目录和路径边界。"""

    def test_rejects_missing_root(self, tmp_path):
        """root 必须是已存在的目录。"""
        missing_root = tmp_path / "missing"

        with pytest.raises(ValueError, match="workspace root"):
            Workspace(missing_root)

    def test_rejects_file_root(self, tmp_path):
        """root 不能是普通文件。"""
        file_root = tmp_path / "file.txt"
        file_root.write_text("not a directory", encoding="utf-8")

        with pytest.raises(ValueError, match="workspace root"):
            Workspace(file_root)

    def test_resolves_relative_path_inside_root(self, tmp_path):
        """相对路径应基于 workspace root 解析为绝对路径。"""
        workspace = Workspace(tmp_path)

        result = workspace.resolve_path("notes/today.md")

        assert result == (tmp_path / "notes" / "today.md").resolve()

    def test_allows_absolute_path_inside_root(self, tmp_path):
        """root 内的绝对路径可以通过解析。"""
        workspace = Workspace(tmp_path)
        inside_path = tmp_path / "src" / "main.py"

        result = workspace.resolve_path(inside_path)

        assert result == inside_path.resolve()

    def test_rejects_absolute_path_outside_root(self, tmp_path):
        """root 外的绝对路径必须被拒绝。"""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        workspace = Workspace(workspace_root)
        outside_path = tmp_path / "outside.txt"

        with pytest.raises(ValueError, match="outside workspace"):
            workspace.resolve_path(outside_path)

    def test_rejects_dot_dot_path_outside_root(self, tmp_path):
        """包含 .. 且解析后越界的路径必须被拒绝。"""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        workspace = Workspace(workspace_root)

        with pytest.raises(ValueError, match="outside workspace"):
            workspace.resolve_path("../outside.txt")

    def test_allows_dot_dot_path_when_resolved_inside_root(self, tmp_path):
        """包含 .. 但最终仍在 root 内的路径可以通过。"""
        workspace = Workspace(tmp_path)

        result = workspace.resolve_path("a/b/../c.txt")

        assert result == (tmp_path / "a" / "c.txt").resolve()

    def test_contains_reports_inside_and_outside_paths(self, tmp_path):
        """contains 只回答路径是否位于 workspace 内，不抛越界异常。"""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        workspace = Workspace(workspace_root)

        assert workspace.contains("inside.txt") is True
        assert workspace.contains("../outside.txt") is False

    def test_rejects_blank_path(self, tmp_path):
        """空路径输入应在 workspace 边界被拒绝。"""
        workspace = Workspace(tmp_path)

        with pytest.raises(ValueError, match="path"):
            workspace.resolve_path(" ")

    def test_rejects_non_string_or_pathlike_path(self, tmp_path):
        """路径输入必须是 str 或 Path，避免坏参数被静默转换。"""
        workspace = Workspace(tmp_path)

        with pytest.raises(TypeError, match="path"):
            workspace.resolve_path(123)
