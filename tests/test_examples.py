import json
import subprocess
import sys
from pathlib import Path


def test_minimal_agent_example_runs_from_repo_root():
    repo_root = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "examples/01_minimal_agent.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "tool:echo: hello" in completed.stdout
    assert "assistant: The tool said: hello" in completed.stdout


def test_tool_schema_example_exports_default_coding_tool_schemas():
    repo_root = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "examples/02_tool_agent.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    schemas = json.loads(completed.stdout)
    schemas_by_name = {
        schema["name"]: schema
        for schema in schemas
    }

    assert list(schemas_by_name) == ["read_file", "write_file", "edit_file", "run_command"]
    assert schemas_by_name["read_file"]["parameters"]["properties"]["path"] == {
        "type": "string",
        "description": "要读取的文件路径；相对路径会基于 workspace_root 解析",
    }
    assert "content" in schemas_by_name["write_file"]["parameters"]["required"]
    assert schemas_by_name["edit_file"]["parameters"]["properties"]["old_text"] == {
        "type": "string",
        "description": "原文件中必须唯一出现的待替换文本；不能为空",
    }
    assert "new_text" in schemas_by_name["edit_file"]["parameters"]["required"]
    assert schemas_by_name["run_command"]["parameters"]["properties"]["command"]["type"] == [
        "string",
        "array",
    ]
    assert "stdout" in schemas_by_name["run_command"]["description"]


def test_observed_tool_run_example_reports_real_read_file_stats():
    """测试 Day 7 示例能展示成功读取、资源拒绝和工具统计。"""
    repo_root = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "examples/03_observed_tool_run.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    report = json.loads(completed.stdout)

    assert report["successful_read"]["ok"] is True
    assert report["successful_read"]["result"] == "hello from observed tool run"
    assert report["successful_read"]["output_truncated"] is False
    assert report["binary_rejection"]["ok"] is False
    assert report["binary_rejection"]["error_type"] == "ValueError"
    assert "file appears to be binary" in report["binary_rejection"]["error_message"]
    assert report["stats"]["read_file"]["calls"] == 2
    assert report["stats"]["read_file"]["successes"] == 1
    assert report["stats"]["read_file"]["failures"] == 1


def test_permission_agent_example_reports_allow_deny_and_ask_paths():
    """测试 Week 4 Day 7 示例能展示 permission gate 的当前真实边界。"""
    repo_root = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "examples/04_permission_agent.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    report = json.loads(completed.stdout)

    assert report["safe_command"]["ok"] is True
    assert report["safe_command"]["result"]["returncode"] == 0
    assert "permission-safe" in report["safe_command"]["result"]["stdout"]

    assert report["denied_command"]["ok"] is False
    assert report["denied_command"]["error_type"] == "PermissionError"
    assert "action=deny" in report["denied_command"]["error_message"]
    assert "recursive_delete" in report["denied_command"]["error_message"]

    assert report["approval_required_command"]["ok"] is False
    assert report["approval_required_command"]["error_type"] == "PermissionError"
    assert "action=ask" in report["approval_required_command"]["error_message"]
    assert "inline_code" in report["approval_required_command"]["error_message"]

    assert report["new_file_write"]["ok"] is True
    assert report["overwrite_file"]["ok"] is False
    assert report["overwrite_file"]["error_type"] == "PermissionError"
    assert "action=ask" in report["overwrite_file"]["error_message"]
    assert "overwrite_existing_file" in report["overwrite_file"]["error_message"]
    assert report["file_after_overwrite_attempt"] == "created by permission example"

    assert report["stats"]["run_command"]["calls"] == 3
    assert report["stats"]["run_command"]["successes"] == 1
    assert report["stats"]["run_command"]["failures"] == 2
    assert report["stats"]["write_file"]["calls"] == 2
    assert report["stats"]["write_file"]["successes"] == 1
    assert report["stats"]["write_file"]["failures"] == 1

    assert report["capability_boundary"] == {
        "interactive_approval": False,
        "approval_resume": False,
        "file_checkpoint_api": True,
        "git_checkpoint_api": True,
        "command_runtime_interface": True,
        "docker_runtime_adapter": True,
        "checkpoint_auto_wired": False,
        # 修改前旧代码：
        # "rollback_auto_wired": False,
        #
        # 问题：Day 6 新增的是文件工具允许执行失败路径的局部 rollback，
        # 不能继续只用全局 rollback_auto_wired=False 表达所有 rollback 状态。
        "file_tool_rollback_on_allowed_failure": True,
        "rollback_auto_wired": False,
        "sandbox": False,
        "audit_auto_wired": False,
    }


def test_checkpoint_rollback_example_reports_restored_file_state_and_boundaries():
    """测试 Week 5 Day 7 示例能展示 checkpoint、失败修改和本地文件 rollback 边界。"""
    repo_root = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "examples/05_checkpoint_rollback.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    report = json.loads(completed.stdout)

    assert report["file_name"] == "demo.txt"
    assert report["original_content"] == "stable workspace content\n"
    assert report["temporary_failed_content"] == "partial failed edit\n"
    assert report["content_after_rollback"] == "stable workspace content\n"
    assert report["restored"] is True
    assert report["simulated_error"] == "simulated failure after local file change"
    assert report["capability_boundary"] == {
        "workspace_file_state_restored": True,
        "network_or_api_side_effects_restored": False,
        "package_install_side_effects_restored": False,
        "background_processes_restored": False,
        "outside_workspace_side_effects_restored": False,
        "shell_or_docker_or_git_auto_rollback": False,
    }
