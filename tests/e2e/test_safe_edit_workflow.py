"""Week 6 Day 6：在临时 Python 仓库中验证安全修改闭环。"""

import json
import sys
from pathlib import Path

import pytest

from pca.tools.base import ToolErrorCode
from pca.tools import file_tools
from pca.tools.file_tools import EditFileTool, ReadFileTool, WriteFileTool
from pca.tools.registry import ToolRegistry
from pca.tools.shell_tools import ShellCommandTool


def test_safe_local_edit_passes_demo_repo_tests(tmp_path: Path) -> None:
    """Agent 应能读取、局部修改并验证一个临时 Python 仓库。"""
    demo_repo = tmp_path / "demo_repo"
    demo_repo.mkdir()
    (demo_repo / "calculator.py").write_text(
        "def add(left: int, right: int) -> int:\n"
        "    return left - right\n",
        encoding="utf-8",
    )
    (demo_repo / "test_calculator.py").write_text(
        "from calculator import add\n\n"
        "def test_add() -> None:\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    audit_path = demo_repo / "permission-audit.jsonl"

    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(EditFileTool(audit_path=audit_path))
    registry.register(ShellCommandTool(audit_path=audit_path))

    initial_test = registry.run(
        "run_command",
        {
            "command": [sys.executable, "-m", "pytest", "test_calculator.py", "-q"],
            "workspace_root": str(demo_repo),
            "timeout_seconds": 30,
        },
    )
    assert initial_test.ok is True
    assert initial_test.result["returncode"] != 0

    read_result = registry.run(
        "read_file",
        {"path": "calculator.py", "workspace_root": str(demo_repo)},
    )
    assert read_result.ok is True
    assert "return left - right" in read_result.result

    edit_result = registry.run(
        "edit_file",
        {
            "path": "calculator.py",
            "old_text": "return left - right",
            "new_text": "return left + right",
            "workspace_root": str(demo_repo),
        },
    )
    assert edit_result.ok is True
    assert edit_result.error_code is None

    final_test = registry.run(
        "run_command",
        {
            "command": [sys.executable, "-m", "pytest", "test_calculator.py", "-q"],
            "workspace_root": str(demo_repo),
            "timeout_seconds": 30,
        },
    )
    assert final_test.ok is True
    assert final_test.result["returncode"] == 0
    assert "return left + right" in (demo_repo / "calculator.py").read_text(
        encoding="utf-8"
    )

    audit_text = audit_path.read_text(encoding="utf-8")
    audit_events = [json.loads(line) for line in audit_text.splitlines()]
    assert len(audit_events) == 3
    assert all(event["executed"] is True for event in audit_events)
    assert "return left + right" not in audit_text
    assert "pytest" not in audit_text

    stats = registry.get_stats()
    assert stats["read_file"]["successes"] == 1
    assert stats["edit_file"]["successes"] == 1
    assert stats["run_command"]["calls"] == 2


def test_overwrite_is_blocked_and_audited(tmp_path: Path) -> None:
    """真实仓库中的覆盖写入应停在 approval gate 前。"""
    target = tmp_path / "calculator.py"
    target.write_text("original\n", encoding="utf-8")
    audit_path = tmp_path / "permission-audit.jsonl"
    registry = ToolRegistry()
    registry.register(WriteFileTool(audit_path=audit_path))

    result = registry.run(
        "write_file",
        {
            "path": "calculator.py",
            "content": "changed\n",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_code is ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert target.read_text(encoding="utf-8") == "original\n"
    event = json.loads(audit_path.read_text(encoding="utf-8"))
    assert event["action"] == "ask"
    assert event["executed"] is False


def test_outside_workspace_is_rejected_without_side_effect(tmp_path: Path) -> None:
    """工作区外 sentinel 必须保持不变。"""
    workspace = tmp_path / "demo_repo"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("sentinel\n", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(WriteFileTool())

    result = registry.run(
        "write_file",
        {
            "path": str(outside),
            "content": "overwritten\n",
            "workspace_root": str(workspace),
        },
    )

    assert result.ok is False
    assert result.error_code is ToolErrorCode.INVALID_ARGUMENT
    assert outside.read_text(encoding="utf-8") == "sentinel\n"


def test_write_failure_restores_demo_repo_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """允许编辑写盘失败后，应恢复 demo repo 的原始文件。"""
    target = tmp_path / "calculator.py"
    original = "def add(left: int, right: int) -> int:\n    return left - right\n"
    target.write_text(original, encoding="utf-8")
    original_write_text = Path.write_text

    def write_then_fail(path: Path, content: str) -> None:
        if path == target.resolve():
            original_write_text(path, content, encoding="utf-8")
            raise OSError("simulated write failure")
        original_write_text(path, content, encoding="utf-8")

    monkeypatch.setattr(file_tools, "_write_text_file", write_then_fail)
    registry = ToolRegistry()
    registry.register(EditFileTool())

    result = registry.run(
        "edit_file",
        {
            "path": "calculator.py",
            "old_text": "return left - right",
            "new_text": "return left + right",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_code is ToolErrorCode.RUNTIME_FAILED
    assert target.read_text(encoding="utf-8") == original


def test_rollback_failure_is_explicit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """写盘和 rollback 都失败时，结果必须暴露 ROLLBACK_FAILED。"""
    target = tmp_path / "calculator.py"
    target.write_text("return 1\n", encoding="utf-8")

    def fail_write(path: Path, content: str) -> None:
        raise OSError("simulated write failure")

    def fail_restore(checkpoint: object) -> None:
        raise OSError("simulated rollback failure")

    monkeypatch.setattr(file_tools, "_write_text_file", fail_write)
    monkeypatch.setattr(file_tools.FileCheckpoint, "restore", fail_restore)
    registry = ToolRegistry()
    registry.register(EditFileTool())

    result = registry.run(
        "edit_file",
        {
            "path": "calculator.py",
            "old_text": "return 1",
            "new_text": "return 2",
            "workspace_root": str(tmp_path),
        },
    )

    assert result.ok is False
    assert result.error_code is ToolErrorCode.ROLLBACK_FAILED
    assert "rollback failed" in result.error_message
