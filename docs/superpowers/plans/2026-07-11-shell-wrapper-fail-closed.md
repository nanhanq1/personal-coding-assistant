# Shell Wrapper Fail-Closed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让已知 cmd/PowerShell shell wrapper 在执行前稳定分类为 `ASK/shell_wrapper`，阻止包装后的未知子命令静默进入真实 runtime。

**Architecture:** 保持现有 `classify_command → PermissionPolicy → ShellCommandTool` 分层不变，只在 ask-rule 边界增加已知 wrapper basename 识别。实现不解析内部命令；wrapper 一律 ASK，由现有 gate、audit 和 ToolResult 错误码链完成 fail-closed 阻断。

**Tech Stack:** Python 3.11、pytest、dataclass/Enum、Mermaid、PowerShell

## Global Constraints

- 仅修复 shell wrapper P0，不处理其他 P1 审计发现。
- 已知 wrapper 固定为 `cmd`、`cmd.exe`、`powershell`、`powershell.exe`、`pwsh`、`pwsh.exe`。
- 字符串/list、大小写、引号和完整路径形式都必须识别。
- wrapper 固定输出 `RiskLevel.ASK`、`matched_rule="shell_wrapper"`。
- 不解析内部命令，不执行真实 cmd/PowerShell/破坏性命令。
- 测试必须先失败再写生产实现。
- 修改生产代码时保留“修改前旧代码”中文注释。
- 不推进 Week 7 Day 1，不修改其他原有 dirty 代码。

---

### Task 1: RED - 建立 wrapper unit、gate 和 safety 回归

**Files:**
- Modify: `tests/test_permissions_risk.py`
- Modify: `tests/test_permissions_shell_gate.py`
- Modify: `tests/safety/test_shell_safety.py`

**Interfaces:**
- Consumes: 现有 `classify_command(...)`、`ShellCommandTool`、`RecordingRuntime` 和 audit fixture。
- Produces: 三层失败测试，锁定 `ASK/shell_wrapper`、approval-required、runtime 未调用和 audit `executed=false`。

- [ ] **Step 1: 写 unit 参数化测试**

在 `tests/test_permissions_risk.py` 增加：

```python
@pytest.mark.parametrize(
    "command",
    [
        "cmd /c del /s /q harmless-target",
        "powershell -Command Remove-Item harmless-target -Recurse -Force",
        "pwsh -Command Get-ChildItem",
        ["cmd.exe", "/c", "echo", "hello"],
        ["PoWeRsHeLl.ExE", "-Command", "Get-ChildItem"],
        [r"C:\Windows\System32\cmd.exe", "/c", "echo", "hello"],
        [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-Command",
            "Get-ChildItem",
        ],
    ],
)
def test_classifies_shell_wrappers_as_ask(command) -> None:
    """shell wrapper 可以隐藏内部行为，默认必须 ASK。"""
    assessment = classify_command(command)

    assert assessment.level is RiskLevel.ASK
    assert assessment.matched_rule == "shell_wrapper"
    assert assessment.reason
```

- [ ] **Step 2: 写 shell gate 参数化测试**

在 `tests/test_permissions_shell_gate.py` 增加：

```python
@pytest.mark.parametrize(
    "command",
    [
        "cmd /c del /s /q harmless-target",
        ["powershell.exe", "-Command", "Get-ChildItem"],
    ],
)
def test_shell_gate_requires_approval_for_shell_wrapper_before_runtime(
    tmp_path,
    command,
) -> None:
    """包装命令必须在 runtime 前转成待审批失败并留下摘要审计。"""
    runtime = RecordingRuntime()
    audit_path = tmp_path / "audit.jsonl"
    registry = ToolRegistry()
    registry.register(ShellCommandTool(runtime=runtime, audit_path=audit_path))

    result = registry.run(
        "run_command",
        {
            "command": command,
            "workspace_root": str(tmp_path),
            "timeout_seconds": 5,
        },
    )

    event = _read_one_audit_event(audit_path)
    assert result.ok is False
    assert result.error_code is tool_base.ToolErrorCode.PERMISSION_APPROVAL_REQUIRED
    assert "shell_wrapper" in result.error_message
    assert runtime.calls == []
    assert event["action"] == "ask"
    assert event["matched_rule"] == "shell_wrapper"
    assert event["executed"] is False
```

同时在该文件顶部增加 `import pytest`。

- [ ] **Step 3: 扩充 safety matrix**

在 `tests/safety/test_shell_safety.py` 的现有参数表增加：

```python
(
    "cmd /c del /s /q harmless-target",
    ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
    "shell_wrapper",
    "ask",
),
(
    ["powershell.exe", "-Command", "Remove-Item", "harmless-target"],
    ToolErrorCode.PERMISSION_APPROVAL_REQUIRED,
    "shell_wrapper",
    "ask",
),
```

这些字符串只交给分类器与 fake runtime gate；测试断言 runtime calls 为空。

- [ ] **Step 4: 运行 RED 并确认正确失败**

Run:

```powershell
E:\python\Scripts\pytest.exe tests\test_permissions_risk.py tests\test_permissions_shell_gate.py tests\safety\test_shell_safety.py -q
```

Expected: 新增 wrapper cases 失败；关键信息为实际 `RiskLevel.SAFE`、`default_safe` 或 runtime 被调用。原有用例继续通过。

---

### Task 2: GREEN - 实现已知 wrapper 默认 ASK

**Files:**
- Modify: `src/pca/permissions/risk.py`
- Test: `tests/test_permissions_risk.py`
- Test: `tests/test_permissions_shell_gate.py`
- Test: `tests/safety/test_shell_safety.py`

**Interfaces:**
- Consumes: `_match_ask_rules(lowered_parts, lowered_text)` 的首 token。
- Produces: `_is_shell_wrapper(executable: str) -> bool`，wrapper 返回稳定 `RiskAssessment(ASK, shell_wrapper)`。

- [ ] **Step 1: 增加 wrapper 常量**

在 `Command` 定义后增加：

```python
SHELL_WRAPPER_EXECUTABLES = {
    "cmd",
    "cmd.exe",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
}
```

- [ ] **Step 2: 在 ASK 规则最前面增加最小判断**

```python
# 修改前旧代码：
# first = lowered_parts[0]
# if first in {"curl", "wget", "invoke-webrequest", "iwr"}:
#     ...
#
# 问题：cmd / PowerShell wrapper 会把真实子命令藏在后续 token 中，
# 只检查 first 会让包装后的危险命令落入 default_safe。
if _is_shell_wrapper(first):
    return RiskAssessment(
        level=RiskLevel.ASK,
        reason="Shell wrapper commands can hide nested command behavior.",
        matched_rule="shell_wrapper",
    )
```

- [ ] **Step 3: 增加 basename helper**

```python
def _is_shell_wrapper(executable: str) -> bool:
    """识别可能隐藏内部命令语义的已知 shell wrapper。"""
    normalized = executable.strip().strip("\"'").replace("\\", "/")
    basename = normalized.rsplit("/", 1)[-1].lower()
    return basename in SHELL_WRAPPER_EXECUTABLES
```

- [ ] **Step 4: 运行 GREEN 聚焦测试**

Run:

```powershell
E:\python\Scripts\pytest.exe tests\test_permissions_risk.py tests\test_permissions_shell_gate.py tests\safety\test_shell_safety.py -q
```

Expected: 全部通过，输出无失败。

- [ ] **Step 5: 运行 permission/shell 回归**

Run:

```powershell
E:\python\Scripts\pytest.exe tests\test_permissions_risk.py tests\test_permissions_policy.py tests\test_permissions_shell_gate.py tests\test_shell_runtime.py tests\safety\test_shell_safety.py -q
```

Expected: 全部通过；直接 DENY/SAFE/network ASK 语义保持不变。

---

### Task 3: 同步 ADR、审计状态和活跃文档

**Files:**
- Modify: `docs/06_ARCHITECTURE_DECISIONS.md`
- Modify: `docs/07_IMPLEMENTATION_LOG.md`
- Modify: `docs/09_NEXT_ACTIONS.md`
- Modify: `docs/18_IMPLEMENTED_MODULE_FLOWS.md`
- Modify: `docs/19_CODE_COMPLETION_AUDIT_2026-07-10.md`
- Modify: `docs/02_DAILY_TASKS.md`

**Interfaces:**
- Consumes: Task 2 的实际测试结果。
- Produces: 真实记录“已知 wrapper 默认 ASK”，不宣称内部解析完成。

- [ ] **Step 1: 新增 ADR-0029**

在 `docs/06_ARCHITECTURE_DECISIONS.md` 顶部新增：

```markdown
## ADR-0029：已知 shell wrapper 默认进入 ASK

- 状态：Accepted
- 日期：2026-07-11
- 决策：`cmd`、`powershell`、`pwsh` 及 `.exe`/完整路径形式统一分类为 `ASK/shell_wrapper`。
- 原因：当前分类器无法可靠解析 Windows quoting、encoded command 和嵌套 wrapper；默认 SAFE 会形成执行前绕过。
- 边界：不解析内部命令，不把 wrapper 宣称为 DENY，不实现 approval resume。
- 证据：unit、shell gate、safety tests 覆盖字符串/list/大小写/完整路径，fake runtime 未调用。
```

- [ ] **Step 2: 更新审计与模块图谱**

- `docs/19...` 的 F-01 总览标为“已于 2026-07-11 通过 known-wrapper ASK 修复”，详细发现追加 resolution，保留原始审计证据和剩余解析边界。
- `docs/18...` 的 permissions 缺口改为“known wrapper 已 fail-closed ASK；仍未解析内部命令/encoded command”。

- [ ] **Step 3: 更新活跃状态文件**

- `docs/07_IMPLEMENTATION_LOG.md` 增加 2026-07-11 P0 remediation、RED/GREEN 命令和结果。
- `docs/09_NEXT_ACTIONS.md` 更新最新聚焦/安全/全量验证和能力边界，但仍保持 Week 7 Day 1 尚未开始、下一指令不变。
- `docs/02_DAILY_TASKS.md` 增加 P0 maintenance note，不把 RepoScanner 标记为已开始。

- [ ] **Step 4: 检查文档边界**

Run:

```powershell
Select-String -Path docs\06_ARCHITECTURE_DECISIONS.md,docs\18_IMPLEMENTED_MODULE_FLOWS.md,docs\19_CODE_COMPLETION_AUDIT_2026-07-10.md -Pattern 'shell_wrapper|不解析|ASK'
Select-String -Path docs\02_DAILY_TASKS.md,docs\09_NEXT_ACTIONS.md -Pattern 'Week 7 Day 1|尚未开始|开始 Week 7 Day 1'
```

Expected: 修复事实与剩余边界均存在，Week 7 状态未推进。

---

### Task 4: 完整验证

**Files:**
- Verify: all modified code, tests, docs

- [ ] **Step 1: 全量测试**

Run:

```powershell
E:\python\Scripts\pytest.exe -q
```

Expected: 旧基线 `206 passed, 1 skipped` 加新增测试后全部通过，跳过数保持可解释。

- [ ] **Step 2: 五个示例**

Run each `examples/01_minimal_agent.py` through `05_checkpoint_rollback.py`。

Expected: 全部退出码 0。

- [ ] **Step 3: 编译验证**

Run:

```powershell
python -m compileall src examples -q
```

Expected: 退出码 0；若仅因 `__pycache__` 沙箱权限失败，按审批流程在沙箱外重跑，不误报语法失败。

- [ ] **Step 4: 工作区与 whitespace**

Run:

```powershell
git diff --check
git status --short
```

Expected: 无真实 whitespace 错误；只出现本计划文件和任务前既有 dirty 文件，CRLF warning 单独记录。

