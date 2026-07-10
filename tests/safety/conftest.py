import json
from pathlib import Path
from typing import Any, Callable

import pytest


class RecordingRuntime:
    """记录 permission gate 是否真的进入命令执行层。"""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(arguments)
        return {
            "stdout": "allowed\n",
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
        }


@pytest.fixture
def recording_runtime() -> RecordingRuntime:
    return RecordingRuntime()


@pytest.fixture
def audit_path(tmp_path: Path) -> Path:
    return tmp_path / "permission-audit.jsonl"


def _read_one_audit_event(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


@pytest.fixture
def read_one_audit_event() -> Callable[[Path], dict[str, Any]]:
    return _read_one_audit_event
