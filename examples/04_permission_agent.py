import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pca.tools import ToolResult, create_coding_tool_registry


def _serialize_tool_result(result: ToolResult) -> dict[str, Any]:
    """把 ToolResult 转成示例可打印的稳定 JSON 结构。"""
    return {
        "ok": result.ok,
        "result": result.result,
        "error_type": result.error_type,
        "error_message": result.error_message,
        "duration_ms": result.duration_ms,
        "trace_id": result.trace_id,
        "tool_call_id": result.tool_call_id,
        "output_truncated": result.output_truncated,
    }


def main() -> None:
    """展示当前真实 permission gate 能力：允许、拒绝、需要审批但不静默执行。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    registry = create_coding_tool_registry()
    with TemporaryDirectory() as workspace_root:
        workspace = Path(workspace_root)
        # 修改前旧代码：
        # "command": ["cmd", "/c", "echo", "permission-safe"],
        #
        # 问题：cmd 是可以隐藏内部子命令的 shell wrapper；P0 修复后必须 ASK，
        # 不能再承担示例中的 SAFE 路径。这里改用直接 Python 版本查询。
        safe_command = registry.run(
            "run_command",
            {
                "command": [sys.executable, "--version"],
                "workspace_root": str(workspace),
                "timeout_seconds": 5,
            },
        )
        denied_command = registry.run(
            "run_command",
            {
                "command": ["rm", "-rf", "danger-zone"],
                "workspace_root": str(workspace),
                "timeout_seconds": 5,
            },
        )
        approval_required_command = registry.run(
            "run_command",
            {
                "command": ["python", "-c", "print('approval-required')"],
                "workspace_root": str(workspace),
                "timeout_seconds": 5,
            },
        )
        wrapper_approval_required_command = registry.run(
            "run_command",
            {
                "command": ["cmd", "/c", "echo", "blocked-wrapper"],
                "workspace_root": str(workspace),
                "timeout_seconds": 5,
            },
        )

        new_file_write = registry.run(
            "write_file",
            {
                "path": "permission-note.txt",
                "content": "created by permission example",
                "workspace_root": str(workspace),
            },
        )
        overwrite_file = registry.run(
            "write_file",
            {
                "path": "permission-note.txt",
                "content": "this overwrite should not be written",
                "workspace_root": str(workspace),
            },
        )
        file_after_overwrite_attempt = (workspace / "permission-note.txt").read_text(
            encoding="utf-8"
        )

    report = {
        "safe_command": _serialize_tool_result(safe_command),
        "denied_command": _serialize_tool_result(denied_command),
        "approval_required_command": _serialize_tool_result(approval_required_command),
        "wrapper_approval_required_command": _serialize_tool_result(
            wrapper_approval_required_command
        ),
        "new_file_write": _serialize_tool_result(new_file_write),
        "overwrite_file": _serialize_tool_result(overwrite_file),
        "file_after_overwrite_attempt": file_after_overwrite_attempt,
        "stats": registry.get_stats(),
        # 修改前旧代码：
        # "rollback_auto_wired": False,
        #
        # 问题：Week 5 Day 6 已经把文件工具的允许执行失败路径接入 FileCheckpoint，
        # 但这不等于 shell/Docker/Git 全链路 rollback 都已完成。
        "capability_boundary": {
            "interactive_approval": False,
            "approval_resume": False,
            "file_checkpoint_api": True,
            "git_checkpoint_api": True,
            "command_runtime_interface": True,
            "docker_runtime_adapter": True,
            "checkpoint_auto_wired": False,
            "file_tool_rollback_on_allowed_failure": True,
            "rollback_auto_wired": False,
            "sandbox": False,
            # 修改前旧代码：
            # "audit_auto_wired": False,
            #
            # 问题：Week 6 Day 4 已让 shell/file permission gate 自动写入摘要
            # audit，继续标记为 false 会让示例错误描述当前能力。
            "audit_auto_wired": True,
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
