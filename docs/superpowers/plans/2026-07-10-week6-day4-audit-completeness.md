# Week 6 Day 4 Audit Completeness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 shell 与文件 permission gate 为 allow、ask、deny 路径留下不泄漏敏感数据的审计证据，并让 allow 路径在审计失败时 fail-closed。

**Architecture:** 在现有 `PermissionPolicy.decide(...)` 后统一构造 `PermissionAuditEvent`。Shell/file gate 只传入工具名、策略决策和风险评估；审计写入先于 allow 副作用。测试可显式注入 `audit_path`；shell 默认 audit 文件在进程工作目录 `.pca/`，不从未验证的 `workspace_root` 派生。

**Tech Stack:** Python 3、pytest、标准库 JSONL、现有 `PermissionAuditEvent`。

## Global Constraints

- 只记录 `timestamp`、`tool_name`、`action`、`risk_level`、`matched_rule`、`reason`、`executed`。
- 不记录完整命令、文件路径/内容、env、token、secret、stdout 或 stderr。
- `ALLOW` 审计失败不得进入 shell runtime 或文件 checkpoint/写盘。
- `ASK`、`DENY` 保留原有 `PermissionError` 语义；不实现审批恢复。
- 不新增文件风险分类规则或 `ToolErrorCode`。

---

### Task 1: 审计事件构造与路径解析

**Files:**
- Modify: `src/pca/permissions/audit.py`
- Test: `tests/test_permissions_audit.py`

**Interfaces:**
- Consumes: `PermissionDecision`、`RiskAssessment`、`append_audit_event(path, event)`。
- Produces: `record_permission_decision(path: Path, tool_name: str, decision: PermissionDecision, *, executed: bool) -> None`。

- [ ] **Step 1: 写失败测试**

```python
def test_record_permission_decision_keeps_only_summary_fields(tmp_path):
    path = tmp_path / "audit.jsonl"
    record_permission_decision(path, "run_command", decision, executed=False)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert set(payload) == {"timestamp", "tool_name", "action", "risk_level", "matched_rule", "reason", "executed"}
```

- [ ] **Step 2: 运行失败测试**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_audit.py -q`

Expected: FAIL，因为 `record_permission_decision` 尚未定义。

- [ ] **Step 3: 最小实现**

```python
def record_permission_decision(path, tool_name, decision, *, executed):
    event = PermissionAuditEvent(
        timestamp=datetime.now(timezone.utc),
        tool_name=tool_name,
        action=decision.action,
        risk_level=decision.assessment.level.value,
        matched_rule=decision.assessment.matched_rule,
        reason=decision.reason,
        executed=executed,
    )
    append_audit_event(path, event)
```

- [ ] **Step 4: 运行通过测试**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_audit.py -q`

Expected: PASS。

### Task 2: Shell gate 审计与 fail-closed

**Files:**
- Modify: `src/pca/tools/shell_tools.py`
- Test: `tests/test_permissions_shell_gate.py`

**Interfaces:**
- Consumes: `record_permission_decision(...)` 与 `PermissionPolicy.decide(...)`。
- Produces: `ShellCommandTool(..., audit_path: Path | None = None)`，默认使用 `<process-cwd>/.pca/permission-audit.jsonl`。

- [ ] **Step 1: 写 allow/ask/deny 和 audit-failure 失败测试**

```python
assert read_audit(audit_path)["action"] == "allow"
assert read_audit(audit_path)["executed"] is True
assert runtime.calls == [arguments]

with monkeypatch.context() as patcher:
    patcher.setattr(shell_tools, "record_permission_decision", raise_os_error)
    result = registry.run("run_command", arguments)
assert result.ok is False
assert runtime.calls == []
```

- [ ] **Step 2: 运行失败测试**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_shell_gate.py -q`

Expected: FAIL，因为构造器没有 `audit_path` 且 gate 未写入审计。

- [ ] **Step 3: 最小实现**

```python
audit_path = self._audit_path or Path.cwd() / ".pca" / "permission-audit.jsonl"
record_permission_decision(audit_path, self.name, decision, executed=decision.action is DecisionAction.ALLOW)
if decision.action is DecisionAction.ALLOW:
    return self._runtime.run(arguments)
raise PermissionError(existing_message)
```

对 `ASK`、`DENY` 用 `try/except OSError` 保留原始 permission 错误；对 `ALLOW` 不捕获审计错误。

- [ ] **Step 4: 运行通过测试**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_shell_gate.py -q`

Expected: PASS。

### Task 3: 文件 gate 审计与 fail-closed

**Files:**
- Modify: `src/pca/tools/file_tools.py`
- Test: `tests/test_permissions_file_risk.py`

**Interfaces:**
- Consumes: 与 Task 2 相同的审计 helper；`_ensure_file_permission(...)` 已拥有工具名、path 和策略对象。
- Produces: `WriteFileTool(..., audit_path: Path | None = None)`、`EditFileTool(..., audit_path: Path | None = None)`，并把审计路径传给 `_ensure_file_permission(...)`。

- [ ] **Step 1: 写失败测试**

```python
assert read_audit(audit_path)["tool_name"] == "write_file"
assert read_audit(audit_path)["executed"] is False
assert existing_file.read_text(encoding="utf-8") == "old content"
```

用测试专用 `DenyPolicy` 返回 `PermissionDecision(DecisionAction.DENY, ..., assessment)`，覆盖文件 gate 的 deny 分支而不改变生产风险规则。对 allow audit-failure，断言目标文件不存在或原内容不变。

- [ ] **Step 2: 运行失败测试**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_file_risk.py -q`

Expected: FAIL，因为 file gate 尚未接入审计。

- [ ] **Step 3: 最小实现**

```python
record_permission_decision(audit_path, tool_name, decision, executed=decision.action is DecisionAction.ALLOW)
if decision.action is DecisionAction.ALLOW:
    return
raise PermissionError(existing_message)
```

`ASK`、`DENY` 的 audit 写入错误只作受控降级，仍然抛出对应 permission 错误；`ALLOW` 的审计错误继续传播以阻止 checkpoint/写盘。

- [ ] **Step 4: 运行通过测试**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_file_risk.py -q`

Expected: PASS。

### Task 4: 集成验证与文档同步

**Files:**
- Modify: `docs/06_ARCHITECTURE_DECISIONS.md`
- Modify: `docs/07_IMPLEMENTATION_LOG.md`
- Modify: `docs/09_NEXT_ACTIONS.md`
- Modify: `docs/17_WEEK6_HARDENING_REPORT.md`

- [ ] **Step 1: 运行聚焦矩阵**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_permissions_audit.py tests\\test_permissions_shell_gate.py tests\\test_permissions_file_risk.py -q`

Expected: PASS。

- [ ] **Step 2: 运行回归集**

Run: `E:\\python\\Scripts\\pytest.exe tests\\test_tools.py tests\\test_retry_policy.py tests\\test_permissions_audit.py tests\\test_permissions_shell_gate.py tests\\test_permissions_file_risk.py tests\\test_rollback_integration.py -q`

Expected: PASS。

- [ ] **Step 3: 运行全量与静态检查**

Run: `E:\\python\\Scripts\\pytest.exe -q; python -m compileall src examples -q; git diff --check`

Expected: 全量 pytest 通过；compileall 无语法错误；diff 无空白错误。

- [ ] **Step 4: 更新真实状态**

记录审计矩阵、fail-closed 边界、验证结果和剩余非目标；Day 4 仅在验证通过后生成面试题，仍等待用户回答才推进到 Day 5。
