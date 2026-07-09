import subprocess

import pytest

from pca.runtime import checkpoints
from pca.runtime.workspace import Workspace


def run_git(repo, *args):
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def init_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init")
    run_git(repo, "config", "user.email", "student@example.com")
    run_git(repo, "config", "user.name", "Student")
    return repo


class TestGitCheckpoint:
    """测试 GitCheckpoint 的 tracked dirty tree diff 快照语义。"""

    def test_create_saves_dirty_tree_diff(self, tmp_path):
        """create 应保存当前 tracked 文件相对 index 的 dirty diff。"""
        repo = init_repo(tmp_path)
        target = repo / "app.py"
        target.write_text("print('before')\n", encoding="utf-8")
        run_git(repo, "add", "app.py")
        target.write_text("print('snapshot')\n", encoding="utf-8")

        checkpoint = checkpoints.GitCheckpoint.create(Workspace(repo))

        assert "print('before')" in checkpoint.diff
        assert "print('snapshot')" in checkpoint.diff

    def test_restore_recovers_tracked_file_to_snapshot_dirty_state(self, tmp_path):
        """restore 应把 tracked 文件恢复到 checkpoint 创建时的 dirty 内容。"""
        repo = init_repo(tmp_path)
        target = repo / "app.py"
        target.write_text("print('before')\n", encoding="utf-8")
        run_git(repo, "add", "app.py")
        target.write_text("print('snapshot')\n", encoding="utf-8")
        checkpoint = checkpoints.GitCheckpoint.create(Workspace(repo))

        target.write_text("print('after')\n", encoding="utf-8")
        checkpoint.restore()

        assert target.read_text(encoding="utf-8") == "print('snapshot')\n"

    def test_create_rejects_non_git_workspace(self, tmp_path):
        """非 git workspace 应在创建 checkpoint 时给出清晰错误。"""
        workspace = Workspace(tmp_path)

        with pytest.raises(ValueError, match="git repository"):
            checkpoints.GitCheckpoint.create(workspace)

    def test_create_reports_missing_git_executable(self, tmp_path, monkeypatch):
        """git 命令不可用时，应返回稳定错误语义，而不是泄漏底层异常。"""
        workspace = Workspace(tmp_path)

        def raise_missing_git(*args, **kwargs):
            raise FileNotFoundError("git")

        monkeypatch.setattr(checkpoints.subprocess, "run", raise_missing_git)

        with pytest.raises(RuntimeError, match="git executable"):
            checkpoints.GitCheckpoint.create(workspace)
