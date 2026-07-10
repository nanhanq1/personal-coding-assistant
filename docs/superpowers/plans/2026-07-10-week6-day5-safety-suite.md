# Week 6 Day 5 Safety Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立 `tests/safety/` 安全回归套件，证明已有 permission、workspace、audit 和 secret redaction 边界不会产生未授权副作用或泄漏敏感值。

**Architecture:** 新套件只通过已有公开工具边界运行：shell 场景经过 `ToolRegistry -> ShellCommandTool` 并注入记录型 runtime；文件场景通过 registry 或文件工具在 `tmp_path` 中验证真实文件状态；secret 场景直接调用 `ShellRuntime` 的本地 list-command 路径。不会修改 `src/`，测试失败即记录为现有能力缺口。

**Tech Stack:** Python 3、pytest、标准库 `json` / `sys` / `uuid`、现有 ToolRegistry、ShellRuntime、file tools。

## Global Constraints

- 不执行真实网络请求、真实删除命令或外部系统操作。
- shell 拒绝路径必须以 `RecordingRuntime.calls == []` 证明未进入 runtime。
- 文件拒绝路径必须断言真实 sentinel 或原文件保持不变。
- 通过 `ToolResult.error_code` 断言稳定语义；只补充固定规则名，不匹配完整异常文案。
- audit 仅断言固定摘要字段；不得把完整命令、文件内容、env 或 secret 写入测试输出。
- secret 使用运行时生成的临时值；脱敏失败时抛出不含该值的固定 `AssertionError`。
- Day 5 不修改风险规则、`ToolErrorCode`、审批恢复、shell workspace 主链或 audit 后端。

---

### Task 1: 建立共享安全测试支撑与 shell 拒绝矩阵

**Files:**
- Create: `tests/safety/conftest.py`
- Create: `tests/safety/test_shell_safety.py`

**Interfaces:**
- Consumes: `ToolRegistry.register(tool)`、`ShellCommandTool(runtime, audit_path)`、`ToolErrorCode`。
- Produces: `RecordingRuntime.run(arguments: dict[str, Any]) -> dict[str, Any]`、`read_one_audit_event(path: Path) -> dict[str, Any]`，供本目录的 shell/file 测试复用。

- [ ] **Step 1: 创建共享 fixture 与审计读取函数**

```python
# tests/safety/conftest.py
import json
from pathlib import Path
from typing import Any, Callable

import pytest


class RecordingRuntime:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(arguments)
        return {"stdout": "allowed\\n", "stderr": "", "returncode": 0, "timed_out": False}


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
```

- [ ] **Step 2: 写 destructive、network 与 inline-code 回归测试**

```python
@pytest.mark.parametrize(
    ("command", "expected_code", "expected_rule"),
    [
        ("rm -rf .", ToolErrorCode.PERMISSION_DENIED, "recursive_delete"),
        ("curl https://example.com", ToolErrorCode.PERMISSION_APPROVAL_REQUIRED, "network_access"),
        ([sys.executable, "-c", "print('blocked')"], ToolErrorCode.PERMISSION_APPROVAL_REQUIRED, "inline_code"),
    ],
)
def test_shell_safety_gate_blocks_before_runtime(tmp_path, audit_path, recording_runtime, read_one_audit_event, command, expected_code, expected_rule):
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=recording_runtime, audit_path=audit_path))
    result = registry.run("run_command", {"command": command, "workspace_root": str(tmp_path), "timeout_seconds": 5})
    event = read_one_audit_event(audit_path)
    assert result.ok is False
    assert result.error_code is expected_code
    assert expected_rule in result.error_message
    assert recording_runtime.calls == []
    assert event["matched_rule"] == expected_rule
    assert event["executed"] is False
```

- [ ] **Step 3: 写 audit secret 边界回归测试**

```python
def test_shell_audit_does_not_include_sensitive_env_value(tmp_path, audit_path, recording_runtime, read_one_audit_event):
    secret = "safety-" + uuid.uuid4().hex
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=recording_runtime, audit_path=audit_path))
    result = registry.run("run_command", {"command": "echo safe", "workspace_root": str(tmp_path), "timeout_seconds": 5, "env": {"PCA_TEST_API_TOKEN": secret}})
    payload = json.dumps(read_one_audit_event(audit_path))
    assert result.ok is True
    assert secret not in payload
```

- [ ] **Step 4: 运行 shell safety 集合**

Run: `E:\python\Scripts\pytest.exe tests\safety\test_shell_safety.py -q`

Expected: PASS；三个拒绝场景均不调用记录型 runtime，安全 allow 场景的 audit 不包含临时 secret。

- [ ] **Step 5: 提交任务变更**

```powershell
git add tests/safety/conftest.py tests/safety/test_shell_safety.py
git commit -m "test: add shell safety regression suite"
```

### Task 2: 添加文件边界与破坏性编辑回归

**Files:**
- Create: `tests/safety/test_file_safety.py`
- Uses: `tests/safety/conftest.py`

**Interfaces:**
- Consumes: `ToolRegistry`、`WriteFileTool`、`EditFileTool`、`ToolErrorCode`、`read_one_audit_event(path)`。
- Produces: 文件安全回归证据；无新的生产接口。

- [ ] **Step 1: 写工作区外 write/edit 测试**

```python
@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("write_file", {"path": "OUTSIDE", "content": "changed"}),
        ("edit_file", {"path": "OUTSIDE", "old_text": "original", "new_text": "changed"}),
    ],
)
def test_file_tools_reject_outside_workspace_without_side_effect(tmp_path, tool_name, arguments):
    outside = tmp_path.parent / "safety-outside-sentinel.txt"
    outside.write_text("original", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    safe_arguments = {**arguments, "path": str(outside), "workspace_root": str(tmp_path)}
    result = registry.run(tool_name, safe_arguments)
    assert result.ok is False
    assert result.error_code is ToolErrorCode.INVALID_ARGUMENT
    assert outside.read_text(encoding="utf-8") == "original"
```

- [ ] **Step 2: 写覆盖和删除式编辑测试**

```python
def test_overwrite_requires_approval_and_preserves_file(tmp_path, audit_path, read_one_audit_event):
    target = tmp_path / "existing.txt"
    target.write_text("original", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(WriteFileTool(audit_path=audit_path))
    result = registry.run("write_file", {"path": "existing.txt", "content": "changed", "workspace_root": str(tmp_path)})
    event = read_one_audit_event(audit_path)
    assert result.error_code is ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert target.read_text(encoding="utf-8") == "original"
    assert event["matched_rule"] == "overwrite_existing_file"
    assert event["executed"] is False


def test_delete_like_edit_requires_approval_and_preserves_file(tmp_path, audit_path, read_one_audit_event):
    target = tmp_path / "module.py"
    target.write_text("important code\\n", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(EditFileTool(audit_path=audit_path))
    result = registry.run("edit_file", {"path": "module.py", "old_text": "important code\\n", "new_text": "", "workspace_root": str(tmp_path)})
    event = read_one_audit_event(audit_path)
    assert result.error_code is ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert target.read_text(encoding="utf-8") == "important code\\n"
    assert event["matched_rule"] == "delete_like_edit"
    assert event["executed"] is False
```

- [ ] **Step 3: 运行文件 safety 集合**

Run: `E:\python\Scripts\pytest.exe tests\safety\test_file_safety.py -q`

Expected: PASS；工作区外 sentinel 和需审批文件均保持原样。

- [ ] **Step 4: 提交任务变更**

```powershell
git add tests/safety/test_file_safety.py
git commit -m "test: cover file safety boundaries"
```

### Task 3: 添加本地 secret redaction 回归

**Files:**
- Create: `tests/safety/test_secret_redaction.py`

**Interfaces:**
- Consumes: `ShellRuntime.run(arguments: dict[str, Any]) -> dict[str, Any]`。
- Produces: 对显式敏感环境变量值不回显的回归证据；无新的生产接口。

- [ ] **Step 1: 写本地解释器脱敏测试**

```python
import sys
import uuid

from pca.runtime.shell_runtime import ShellRuntime


def test_shell_runtime_redacts_sensitive_env_value_without_echoing_secret(tmp_path):
    secret = "safety-" + uuid.uuid4().hex
    result = ShellRuntime().run(
        {
            "command": [sys.executable, "-c", "import os; print(os.environ['PCA_TEST_API_TOKEN'])"],
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
            "env": {"PCA_TEST_API_TOKEN": secret},
        }
    )
    if result["stdout"] != "[REDACTED]\\n":
        raise AssertionError("shell runtime did not redact sensitive environment output")
    if secret in result["stderr"]:
        raise AssertionError("shell runtime returned a sensitive value in stderr")
```

- [ ] **Step 2: 运行脱敏测试**

Run: `E:\python\Scripts\pytest.exe tests\safety\test_secret_redaction.py -q`

Expected: PASS；本地解释器输出为 `[REDACTED]`，不会访问网络。

- [ ] **Step 3: 提交任务变更**

```powershell
git add tests/safety/test_secret_redaction.py
git commit -m "test: cover shell secret redaction"
```

### Task 4: 运行总体验证并同步 Day 5 文档

**Files:**
- Modify: `EVALUATION.md`
- Modify: `docs/07_IMPLEMENTATION_LOG.md`
- Modify: `docs/09_NEXT_ACTIONS.md`
- Modify: `docs/17_WEEK6_HARDENING_REPORT.md`
- Modify: `docs/02_DAILY_TASKS.md`

**Interfaces:**
- Consumes: `tests/safety/` 的完整回归结果和现有五个示例。
- Produces: Day 5 的真实验证记录与“面试题待回答”的下一步门禁。

- [ ] **Step 1: 运行安全集与全量回归**

Run: `E:\python\Scripts\pytest.exe tests\safety -q; E:\python\Scripts\pytest.exe -q`

Expected: safety suite 全绿；全量测试通过，计数以命令实际输出为准。

- [ ] **Step 2: 运行五个示例和编译检查**

Run: `python examples\01_minimal_agent.py; python examples\02_tool_agent.py; python examples\03_observed_tool_run.py; python examples\04_permission_agent.py; python examples\05_checkpoint_rollback.py; python -m compileall src examples -q`

Expected: 五个示例均成功；如 compileall 仅因沙箱写入 `__pycache__` 失败，记录为环境权限问题并在获准后重跑，不将其误判为语法回归。

- [ ] **Step 3: 更新文档事实**

在 `EVALUATION.md` 的 Safety 层写明套件不执行真实网络或删除命令，并使用注入 runtime 与 `tmp_path` 证明副作用边界；在三个 Week 6 状态文档记录测试数量、验证日期、覆盖矩阵和仍未覆盖的 sandbox/approval-resume 边界。`docs/02_DAILY_TASKS.md` 改为 Day 5 已完成但面试题待回答；不得推进 Day 6。

- [ ] **Step 4: 运行差异检查并提交文档**

Run: `git diff --check`

Expected: 无实际空白错误；Windows CRLF 提示单独记录，不视为内容失败。

```powershell
git add EVALUATION.md docs/02_DAILY_TASKS.md docs/07_IMPLEMENTATION_LOG.md docs/09_NEXT_ACTIONS.md docs/17_WEEK6_HARDENING_REPORT.md
git commit -m "docs: record week6 day5 safety suite"
```
