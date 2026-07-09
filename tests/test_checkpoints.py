import pytest

from pca.runtime import checkpoints
from pca.runtime.workspace import Workspace


class TestFileCheckpoint:
    """测试 FileCheckpoint 的本地文件快照和恢复语义。"""

    def test_restore_recovers_modified_file_content(self, tmp_path):
        """已存在文件被修改后，restore 应恢复到快照时的内容。"""
        workspace = Workspace(tmp_path)
        target = tmp_path / "notes.txt"
        target.write_text("before", encoding="utf-8")
        checkpoint = checkpoints.FileCheckpoint.create(workspace, ["notes.txt"])

        target.write_text("after", encoding="utf-8")
        checkpoint.restore()

        assert target.read_text(encoding="utf-8") == "before"

    def test_restore_recreates_file_deleted_after_snapshot(self, tmp_path):
        """快照时存在的文件被删除后，restore 应重新创建文件和内容。"""
        workspace = Workspace(tmp_path)
        target = tmp_path / "src" / "main.py"
        target.parent.mkdir()
        target.write_text("print('hello')", encoding="utf-8")
        checkpoint = checkpoints.FileCheckpoint.create(workspace, ["src/main.py"])

        target.unlink()
        checkpoint.restore()

        assert target.read_text(encoding="utf-8") == "print('hello')"

    def test_restore_removes_tracked_file_created_after_snapshot(self, tmp_path):
        """快照时不存在的被跟踪路径，如果后来新建文件，restore 应清理它。"""
        workspace = Workspace(tmp_path)
        target = tmp_path / "generated.txt"
        checkpoint = checkpoints.FileCheckpoint.create(workspace, ["generated.txt"])

        target.write_text("temporary output", encoding="utf-8")
        checkpoint.restore()

        assert target.exists() is False

    def test_create_rejects_path_outside_workspace(self, tmp_path):
        """快照路径必须复用 Workspace.resolve_path 的越界拒绝规则。"""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        workspace = Workspace(workspace_root)

        with pytest.raises(ValueError, match="outside workspace"):
            checkpoints.FileCheckpoint.create(workspace, ["../outside.txt"])
