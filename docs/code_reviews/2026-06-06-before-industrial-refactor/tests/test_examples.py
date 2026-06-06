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
