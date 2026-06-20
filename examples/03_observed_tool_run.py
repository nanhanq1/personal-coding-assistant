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
    """展示当前真实工具观测能力：成功读取、资源拒绝和调用统计。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    registry = create_coding_tool_registry()
    with TemporaryDirectory() as workspace_root:
        workspace = Path(workspace_root)
        text_file = workspace / "notes.txt"
        binary_file = workspace / "binary.bin"
        text_file.write_text("hello from observed tool run", encoding="utf-8")
        binary_file.write_bytes(b"text-prefix\x00binary-suffix")

        successful_read = registry.run(
            "read_file",
            {
                "path": "notes.txt",
                "workspace_root": str(workspace),
            },
        )
        binary_rejection = registry.run(
            "read_file",
            {
                "path": "binary.bin",
                "workspace_root": str(workspace),
            },
        )

    report = {
        "successful_read": _serialize_tool_result(successful_read),
        "binary_rejection": _serialize_tool_result(binary_rejection),
        "stats": registry.get_stats(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
