# Stable Invalid Input Errors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 ToolRegistry 与 approval 对象对非法输入提供稳定、可测试且不会泄漏实现细节的错误契约。

**Architecture:** 在 `ToolRegistry.run(...)` 的统一边界规范化失败统计键，同时保留 `ToolResult.from_exception(...)` 的错误码映射；在 approval 不可变数据对象的 `__post_init__` 中按“类型→非空/时区→关系”顺序校验。两个修改相互独立，共享最终回归与文档收口。

**Tech Stack:** Python 3.13、dataclasses、datetime、pytest。

## Global Constraints

- 必须保留中文“修改前旧代码”注释。
- 非法工具名统一统计到 `<invalid-tool-name>`，不得记录原始值。
- Approval 时间必须是 timezone-aware `datetime`。
- 不实现 audit 生命周期或 approval resume，不推进 Week 7 Day 1。

---

### Task 1: ToolRegistry 非法名称稳定结果

**Files:**
- Modify: `tests/test_tools.py`
- Modify: `src/pca/tools/registry.py`

**Interfaces:**
- Consumes: `ToolRegistry.run(name, arguments, *, trace_id=None, tool_call_id=None) -> ToolResult`
- Produces: `INVALID_TOOL_STATS_KEY = "<invalid-tool-name>"` 与稳定失败统计键选择逻辑。

- [ ] **Step 1: 写失败测试**

新增参数化测试，传入 `[]`、`{}`、`None`、`""`、`"   "`，断言返回 `INVALID_ARGUMENT`、保留 trace、handler 不执行，且 stats 只出现 `<invalid-tool-name>`；保留未知合法字符串的 `UNKNOWN_TOOL` 断言。

- [ ] **Step 2: 运行 RED**

Run: `E:\python\Scripts\pytest.exe tests\test_tools.py -k "invalid_tool_name or unknown_tool" -q`

Expected: list/dict 用例因 `_stats.setdefault(...)` 收到不可哈希键而失败，其他非法输入的统计键契约失败。

- [ ] **Step 3: 最小实现**

在 `registry.py` 增加固定统计键，并在 `run(...)` 进入执行前选择安全统计键：有效非空字符串使用原名称，其他输入使用 `<invalid-tool-name>`；异常与成功路径均只把安全键交给 `_record_stats(...)`。

- [ ] **Step 4: 运行 GREEN**

Run: `E:\python\Scripts\pytest.exe tests\test_tools.py -k "invalid_tool_name or unknown_tool" -q`

Expected: PASS。

### Task 2: Approval 严格字段与时间校验

**Files:**
- Modify: `tests/test_permissions_approval.py`
- Modify: `src/pca/permissions/approval.py`

**Interfaces:**
- Consumes: `ApprovalRequest(...)`、`ApprovalDecision(...)`、`approve(...)`、`reject(...)`、`is_expired(now=None)`。
- Produces: 稳定 `TypeError` / `ValueError` 契约及 timezone-aware datetime 边界。

- [ ] **Step 1: 写失败测试**

新增参数化测试覆盖字符串字段非字符串/空白、`approved=1`、错误时间类型、naive datetime、`is_expired(...)` 错误时间，以及有效 UTC/非 UTC aware datetime。

- [ ] **Step 2: 运行 RED**

Run: `E:\python\Scripts\pytest.exe tests\test_permissions_approval.py -q`

Expected: 当前代码出现 `AttributeError` 或错误接受非法值，测试失败。

- [ ] **Step 3: 最小实现**

新增 `_validate_non_empty_string(field_name, value)` 与 `_validate_aware_datetime(field_name, value)`；两个 dataclass 在 `__post_init__` 中依次调用，并严格验证 `approved`。`is_expired(...)` 对传入的显式 now 复用时间校验。

- [ ] **Step 4: 运行 GREEN**

Run: `E:\python\Scripts\pytest.exe tests\test_permissions_approval.py -q`

Expected: PASS。

### Task 3: 回归、文档与验收

**Files:**
- Modify: `docs/02_DAILY_TASKS.md`
- Modify: `docs/06_ARCHITECTURE_DECISIONS.md`
- Modify: `docs/07_IMPLEMENTATION_LOG.md`
- Modify: `docs/09_NEXT_ACTIONS.md`
- Modify: `docs/19_CODE_COMPLETION_AUDIT_2026-07-10.md`

**Interfaces:**
- Consumes: Task 1 与 Task 2 的稳定错误契约。
- Produces: ADR、审计整改状态和真实验证证据。

- [ ] **Step 1: 运行相关回归**

Run: `E:\python\Scripts\pytest.exe tests\test_tools.py tests\test_permissions_approval.py tests\test_retry_policy.py tests\test_agent_loop.py -q`

Expected: PASS。

- [ ] **Step 2: 同步文档**

新增 ADR，记录非法工具名统计桶和 approval aware-datetime 契约；将 F-02/F-03 标记为已整改，同时明确 F-04/F-05 未包含。

- [ ] **Step 3: 完整验收**

Run: `E:\python\Scripts\pytest.exe -q`

Run: 依次运行 `examples/01_minimal_agent.py` 至 `examples/05_checkpoint_rollback.py`

Run: `E:\python\python.exe -m compileall src examples -q`

Run: `git diff --check`

Expected: 全部退出码 0；如 compileall 仅因沙箱 `__pycache__` 写权限失败，按项目既有流程申请沙箱外重跑。
