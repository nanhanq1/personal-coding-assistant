from pathlib import Path

import pytest

from pca.permissions.policy import DecisionAction, PermissionDecision
from pca.tools import file_tools


def test_allowed_edit_rolls_back_file_when_write_fails_after_partial_change(tmp_path, monkeypatch):
    """允许的小范围 edit_file 如果写盘中途失败，应恢复执行前文件内容。"""
    target = tmp_path / "module.py"
    original = "def greet():\n    return 'hello'\n"
    partial = "def greet():\n    return 'hi'\n"
    target.write_text(original, encoding="utf-8")
    original_write_text = Path.write_text

    def write_then_fail(path, data, *args, **kwargs):
        if path == target.resolve():
            original_write_text(path, data, *args, **kwargs)
            raise RuntimeError("simulated write failure after partial edit")
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", write_then_fail)

    with pytest.raises(RuntimeError, match="simulated write failure"):
        file_tools.EditFileTool().run(
            {
                "path": "module.py",
                "old_text": "return 'hello'",
                "new_text": "return 'hi'",
                "workspace_root": str(tmp_path),
            }
        )

    assert target.read_text(encoding="utf-8") == original
    assert target.read_text(encoding="utf-8") != partial


def test_allowed_new_file_write_rolls_back_created_file_when_write_fails(tmp_path, monkeypatch):
    """允许的新建 write_file 如果写盘中途失败，应删除半成品文件。"""
    target = tmp_path / "generated.txt"
    original_write_text = Path.write_text

    def write_then_fail(path, data, *args, **kwargs):
        if path == target.resolve():
            original_write_text(path, data, *args, **kwargs)
            raise RuntimeError("simulated write failure after partial create")
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", write_then_fail)

    with pytest.raises(RuntimeError, match="simulated write failure"):
        file_tools.WriteFileTool().run(
            {
                "path": "generated.txt",
                "content": "temporary generated output",
                "workspace_root": str(tmp_path),
            }
        )

    assert target.exists() is False


def test_ask_file_change_does_not_create_checkpoint(tmp_path, monkeypatch):
    """未审批 ASK 会在副作用路径前停止，不应创建 checkpoint。"""
    target = tmp_path / "existing.txt"
    original = "old content"
    target.write_text(original, encoding="utf-8")

    def fail_if_checkpoint_is_created(*args, **kwargs):
        raise AssertionError("ASK should not create a checkpoint")

    monkeypatch.setattr(file_tools.FileCheckpoint, "create", fail_if_checkpoint_is_created)

    with pytest.raises(PermissionError, match="overwrite_existing_file"):
        file_tools.WriteFileTool().run(
            {
                "path": "existing.txt",
                "content": "new content",
                "workspace_root": str(tmp_path),
            }
        )

    assert target.read_text(encoding="utf-8") == original


def test_deny_file_change_does_not_create_checkpoint(tmp_path, monkeypatch):
    """DENY 会在副作用路径前停止，不应创建 checkpoint。"""
    target = tmp_path / "new.txt"

    class DenyPolicy:
        def decide(self, assessment):
            return PermissionDecision(
                action=DecisionAction.DENY,
                reason="blocked by test policy",
                assessment=assessment,
            )

    def fail_if_checkpoint_is_created(*args, **kwargs):
        raise AssertionError("DENY should not create a checkpoint")

    monkeypatch.setattr(file_tools.FileCheckpoint, "create", fail_if_checkpoint_is_created)

    with pytest.raises(PermissionError, match="Permission denied"):
        file_tools.WriteFileTool(permission_policy=DenyPolicy()).run(
            {
                "path": "new.txt",
                "content": "new content",
                "workspace_root": str(tmp_path),
            }
        )

    assert target.exists() is False
