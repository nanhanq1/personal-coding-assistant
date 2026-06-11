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

    assert list(schemas_by_name) == ["read_file", "write_file", "run_command"]
    assert schemas_by_name["read_file"]["parameters"]["properties"]["path"] == {
        "type": "string",
        "description": "要读取的文件路径；相对路径会基于 workspace_root 解析",
    }
    assert "content" in schemas_by_name["write_file"]["parameters"]["required"]
    assert schemas_by_name["run_command"]["parameters"]["properties"]["command"]["type"] == [
        "string",
        "array",
    ]
    assert "stdout" in schemas_by_name["run_command"]["description"]
