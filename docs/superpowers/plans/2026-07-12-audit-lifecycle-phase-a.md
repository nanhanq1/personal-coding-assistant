# Audit Lifecycle Phase A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 operation_id 和明确执行阶段替代含糊的 executed 布尔值，并为审计持久化失败提供不可重试的稳定错误语义。

**Architecture:** permission decision 与 tool execution 使用两种摘要事件写入同一 JSONL，通过 operation_id 关联。shell/file wrapper 在副作用前后写入阶段事件；文件失败路径保证 rollback 不被审计异常打断。

**Tech Stack:** Python 3.13、dataclasses、Enum、UUID、JSONL、pytest。

## Global Constraints

- 修改生产代码必须保留中文“修改前旧代码”注释。
- 审计事件不得包含原始命令、路径、文件内容、输出、异常消息或 secret。
- 副作用前 audit 失败必须 fail-closed；副作用后 audit 失败必须返回 `AUDIT_FAILED`。
- F-04b trace/tool_call context、F-05 CI 和 Week 7 RepoScanner 不在范围内。

---

### Task 1: Audit 事件模型和稳定错误码

**Files:**
- Modify: `tests/test_permissions_audit.py`
- Modify: `tests/test_tools.py`
- Modify: `tests/test_retry_policy.py`
- Modify: `src/pca/permissions/audit.py`
- Modify: `src/pca/tools/base.py`
- Modify: `src/pca/tools/retry.py`

**Interfaces:**
- Produces: `ToolExecutionPhase`、`ToolExecutionAuditEvent`、`AuditPersistenceError`、`new_operation_id()`、`record_tool_execution_event(...)`、`ToolErrorCode.AUDIT_FAILED`。

- [ ] **Step 1:** 写事件 schema、序列化、operation id、AUDIT_FAILED 映射和不可重试 RED 测试。
- [ ] **Step 2:** 运行 `E:\python\Scripts\pytest.exe tests\test_permissions_audit.py tests\test_tools.py tests\test_retry_policy.py -q`，确认因新 API/字段缺失失败。
- [ ] **Step 3:** 最小实现事件、异常、错误码和 retry 映射；移除 `executed`，使用 `authorized`。
- [ ] **Step 4:** 重跑同一命令确认 GREEN。

### Task 2: Shell 生命周期

**Files:**
- Modify: `tests/test_permissions_shell_gate.py`
- Modify: `tests/safety/test_shell_safety.py`
- Modify: `src/pca/tools/shell_tools.py`

**Interfaces:**
- Consumes: Task 1 audit API。
- Produces: decision/start/success/failure 顺序与 post-side-effect audit failure 语义。

- [ ] **Step 1:** 写 ASK/DENY、ALLOW success、runtime failure、pre/post audit failure RED 测试。
- [ ] **Step 2:** 运行 shell gate 与 safety 聚焦测试，确认旧单事件实现失败。
- [ ] **Step 3:** 在 `ShellCommandTool._run(...)` 生成一次 operation_id，按设计写入事件并映射审计失败。
- [ ] **Step 4:** 重跑聚焦测试确认 GREEN。

### Task 3: File 生命周期与 rollback

**Files:**
- Modify: `tests/test_permissions_file_risk.py`
- Modify: `tests/test_rollback_integration.py`
- Modify: `tests/safety/test_file_safety.py`
- Modify: `src/pca/tools/file_tools.py`

**Interfaces:**
- Consumes: Task 1 audit API。
- Produces: decision/start/success/failed/rolled_back/rollback_failed 顺序，且 audit 失败不跳过 rollback。

- [ ] **Step 1:** 写允许成功、写盘失败并回滚、rollback 失败、outcome audit 失败 RED 测试。
- [ ] **Step 2:** 运行 file permission/rollback/safety 聚焦测试，确认缺少生命周期事件。
- [ ] **Step 3:** 让 permission helper 接收 operation_id，让 checkpoint helper记录阶段并保证 rollback 优先执行。
- [ ] **Step 4:** 重跑聚焦测试确认 GREEN。

### Task 4: 示例、文档和完整验收

**Files:**
- Modify: `examples/04_permission_agent.py`
- Modify: `tests/test_examples.py`
- Modify: `docs/02_DAILY_TASKS.md`
- Modify: `docs/06_ARCHITECTURE_DECISIONS.md`
- Modify: `docs/07_IMPLEMENTATION_LOG.md`
- Modify: `docs/09_NEXT_ACTIONS.md`
- Modify: `docs/18_IMPLEMENTED_MODULE_FLOWS.md`
- Modify: `docs/19_CODE_COMPLETION_AUDIT_2026-07-10.md`

- [ ] **Step 1:** 更新示例断言为 authorized + lifecycle，并运行 example 聚焦测试。
- [ ] **Step 2:** 同步 ADR、流程、审计整改状态和真实测试数字，不推进 Week 7。
- [ ] **Step 3:** 运行相关 permission/tools/rollback/safety 回归。
- [ ] **Step 4:** 运行全量 pytest、5 个示例、compileall 和 `git diff --check`。
