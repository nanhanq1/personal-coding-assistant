# Implementation Log

本文件只保留当前活跃实现记录。历史记录归档在 `docs/archive/implementation_log/`。

## 2026-07-10

### Week 6 Day 4 Audit 完整性

### 本次完成

- 按 TDD 先新增审计事件、shell gate、file gate 和示例真实性测试，分别确认缺少 helper、缺少 `audit_path` 注入和旧示例状态导致的 RED。
- 新增 `record_permission_decision(...)`，仅把 `PermissionDecision` 的摘要写成 `PermissionAuditEvent` JSONL。
- shell、`write_file`、`edit_file` gate 现在覆盖 `ALLOW`、`ASK`、`DENY` 审计；默认文件分类不产生 `DENY`，用测试专用策略验证该分支。
- `ALLOW` 在审计写入失败时 fail-closed，runtime 或写盘均不会发生；`ASK` / `DENY` 保持原有 `PermissionError` 且不执行。
- 审计记录不包含完整命令、文件路径/内容、env、token、secret、stdout 或 stderr；`executed` 表示已获准进入副作用路径，不表示副作用成功。
- 修复默认 shell audit 路径不能从未验证 `workspace_root` 派生的问题，避免创建不存在目录或改变 runtime 的原有参数校验；默认写至进程工作目录 `.pca/permission-audit.jsonl`，该目录已忽略版本控制。
- 更新 permission 示例，使 `audit_auto_wired` 与实际实现一致。
- 新增 ADR-0027 与 Day 4 设计/实施计划。

### 验证

- `E:\python\Scripts\pytest.exe tests\test_permissions_audit.py -q`：`4 passed`。
- `E:\python\Scripts\pytest.exe tests\test_permissions_shell_gate.py -q`：`7 passed`。
- `E:\python\Scripts\pytest.exe tests\test_permissions_file_risk.py -q`：`9 passed`。
- `E:\python\Scripts\pytest.exe tests\test_permissions_audit.py tests\test_permissions_shell_gate.py tests\test_permissions_file_risk.py -q`：`20 passed`。
- `E:\python\Scripts\pytest.exe tests\test_tools.py tests\test_retry_policy.py tests\test_permissions_audit.py tests\test_permissions_shell_gate.py tests\test_permissions_file_risk.py tests\test_rollback_integration.py -q`：`69 passed`。
- `E:\python\Scripts\pytest.exe tests\test_shell_runtime.py -q`：`25 passed`。
- `E:\python\Scripts\pytest.exe tests\test_examples.py::test_permission_agent_example_reports_allow_deny_and_ask_paths -q`：`1 passed`。
- `E:\python\Scripts\pytest.exe -q`：`190 passed, 1 skipped`。
- 五个示例均通过；`examples\04_permission_agent.py` 现在如实输出 `audit_auto_wired=true`。
- `python -m compileall src examples -q` 沙箱内受 `__pycache__` 写权限限制；批准后外部重跑通过且无输出。`git diff --check` 仅输出 Windows CRLF 警告，无空白错误。

### 下一步

- Day 4 面试题已按用户确认归档为第 40 天记录；当前进入 Week 6 Day 5 Safety suite。

### Week 6 Day 5 Safety suite

### 本次完成

- 新增 `tests/safety/`，把 shell permission gate、file workspace/risk gate、audit 摘要和 shell 输出脱敏组织为独立安全回归层。
- shell 用 `RecordingRuntime` 验证 `rm -rf`、`curl` 和 `python -c` 分别命中 `recursive_delete`、`network_access` 和 `inline_code`，且都没有进入 runtime。
- 文件用真实临时 sentinel 验证工作区外路径、覆盖已有文件和删除式编辑均没有未授权写盘。
- secret redaction 用本地 Python list-command 验证敏感环境变量只返回 `[REDACTED]`；audit JSONL 不包含敏感值。
- 未修改风险规则、稳定错误码、审批恢复、完整 sandbox 或 runtime 主链；当前测试仅记录已有行为证据。

### 验证

- `E:\python\Scripts\pytest.exe tests\safety -q`：`9 passed`。
- `E:\python\Scripts\pytest.exe -q`：`199 passed, 1 skipped`。
- 五个示例均通过；permission 示例仍输出 `audit_auto_wired=true`，checkpoint 示例仍输出 `restored=true`。
- `python -m compileall src examples -q`：通过，无输出。
- `git diff --check`：通过；仅有 Windows CRLF 转换提示，无实际空白错误。

### 仍未覆盖的真实安全边界

- 不执行真实网络请求、真实删除命令或外部系统操作；当前证据是本地 gate 和临时文件边界。
- `ASK` 仍不支持批准后恢复，Docker 仍不是默认 sandbox，shell/Docker/Git 副作用仍未自动 rollback。
- Day 5 面试题尚未回答和归档，完成面试门禁前不推进 Week 6 Day 6。

### Week 6 Day 3 Retry / timeout policy

### 本次完成

- 按 TDD 新增 `tests/test_retry_policy.py`，先确认 `pca.tools.retry` 不存在导致 RED。
- 新增 `src/pca/tools/retry.py`，提供 `RetryDecision`、`RetryPolicy.decide(...)` 和 `should_retry(...)`。
- retry policy 基于 `ToolResult.error_code` 判断，不解析自然语言错误消息。
- `RUNTIME_FAILED` 只作为可重试候选，不自动重复执行工具。
- `PERMISSION_DENIED`、`PERMISSION_APPROVAL_REQUIRED`、`INVALID_ARGUMENT`、`UNKNOWN_TOOL`、`CHECKPOINT_FAILED` 和 `ROLLBACK_FAILED` 默认不可重试。
- 从 `pca.tools` 包入口导出 retry policy API。
- 新增 ADR-0026，记录 Day 3 只做策略判断，不接入自动 retry 主链。

### 验证

- RED：`E:\python\Scripts\pytest.exe tests\test_retry_policy.py -q` 失败于 `ModuleNotFoundError: No module named 'pca.tools.retry'`。
- `E:\python\Scripts\pytest.exe tests\test_retry_policy.py -q`：`6 passed`。
- `E:\python\Scripts\pytest.exe tests\test_tools.py tests\test_retry_policy.py -q`：`44 passed`。
- `E:\python\Scripts\pytest.exe tests\test_retry_policy.py tests\test_tools.py tests\test_permissions_shell_gate.py tests\test_permissions_file_risk.py tests\test_rollback_integration.py -q`：`57 passed`。
- `E:\python\Scripts\pytest.exe -q`：`181 passed, 1 skipped`。
- `python examples\01_minimal_agent.py`：通过。
- `python examples\02_tool_agent.py`：通过，输出工具 schema。
- `python examples\03_observed_tool_run.py`：通过，保持旧观察输出兼容。
- `python examples\04_permission_agent.py`：通过，保持 permission 示例输出兼容。
- `python examples\05_checkpoint_rollback.py`：通过，输出 `restored=true`。
- `python -m compileall src examples -q`：沙箱内因 `__pycache__` 写入权限失败；批准后外部重跑通过，无输出。

### 下一步

- 用户已明确确认“直接将答案作为用户的回答”。
- 已将 Week 6 Day 3 面试题归档为第 39 天记录。
- 已修正 `docs/Compilation-of-Interview-Questions.md` 末尾第 36-38 天顺序漂移和重复第 36 天记录。
- 已同步 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。
- 当前推进 Week 6 Day 4：Audit 完整性。

## 2026-07-09

### Week 6 Day 2 Tool Runtime 错误分类

### 本次完成

- 按 TDD 增加 `ToolErrorCode` focused tests，先看到缺少错误码字段的 RED。
- 在 `src/pca/tools/base.py` 中新增 `ToolErrorCode` 和 `ToolResult.error_code`。
- `ToolResult.from_exception(...)` 现在把参数错误、未知工具、permission ASK/DENY、runtime、checkpoint 和 rollback 失败映射为稳定错误码。
- 从 `pca.tools` 包入口导出 `ToolErrorCode`。
- 保持 `error_type`、`error_message`、`ToolResult.__str__()` 和现有示例 JSON 输出兼容。
- 新增 ADR-0025，记录 Day 2 只做错误分类，不实现 retry、audit 自动接入或 sandbox。

### 验证

- `E:\python\Scripts\pytest.exe tests\test_tools.py -q`：`38 passed`。
- `E:\python\Scripts\pytest.exe tests\test_permissions_shell_gate.py tests\test_permissions_file_risk.py tests\test_rollback_integration.py -q`：`13 passed`。
- `E:\python\Scripts\pytest.exe -q`：`175 passed, 1 skipped`。
- `python examples\01_minimal_agent.py`：通过。
- `python examples\02_tool_agent.py`：通过，输出工具 schema。
- `python examples\03_observed_tool_run.py`：通过，保持旧观察输出兼容。
- `python examples\04_permission_agent.py`：通过，保持 permission 示例输出兼容。
- `python examples\05_checkpoint_rollback.py`：通过，输出 `restored=true`。
- `python -m compileall src examples -q`：通过，无输出；沙箱内写 `.pyc` 受限，已在批准后外部验证。
- `git diff --check`：通过，仅有 Windows CRLF 提示。

### 下一步

- 用户已明确确认“直接将答案作为用户的回答”。
- 已将 Week 6 Day 2 面试题归档为第 38 天记录。
- 已同步 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/09_NEXT_ACTIONS.md` 和 `docs/Compilation-of-Interview-Questions.md`。
- 当前推进 Week 6 Day 3：Retry / timeout policy。

### Week 6 Day 1 Tool Runtime 加固现状评估

### 本次完成

- 读取教学规则、当前状态、日任务、周 Sprint、工业级标准、已实现架构、ADR-0014 到 ADR-0024 和教学流程。
- 核对 Week 4-5 的 permission、workspace、checkpoint、runtime 和 rollback 当前源码证据。
- 新增 `docs/17_WEEK6_HARDENING_REPORT.md`，按 9 个工业级维度列出当前状态、证据、差距和 P0/P1/P2 优先级。
- 更新 `docs/04_RESOURCE_LIBRARY.md`，补充 Week 6 Day 1 的官方资料和视频入口。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/09_NEXT_ACTIONS.md` 和 `docs/INDEX.md`。

### 验证

- `E:\python\Scripts\pytest.exe -q`：`168 passed, 1 skipped`。
- `python examples\01_minimal_agent.py`：通过。
- `python examples\02_tool_agent.py`：通过，输出工具 schema。
- `python examples\03_observed_tool_run.py`：通过，展示成功读取、二进制拒绝和 stats。
- `python examples\04_permission_agent.py`：通过，展示 shell/file gate 和能力边界。
- `python examples\05_checkpoint_rollback.py`：通过，输出 `restored=true`。
- `python -m compileall src examples -q`：通过，无输出。

### 下一步

- 用户已明确确认“直接将答案作为用户的回答”。
- 已将 Week 6 Day 1 面试题归档为第 37 天记录。
- 已同步 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/09_NEXT_ACTIONS.md` 和 `docs/Compilation-of-Interview-Questions.md`。
- 当前推进 Week 6 Day 2：错误分类。

## 2026-07-04

### 教学文档与记忆文档维护

### 本次完成

- 新增 `docs/16_TEACHING_WORKFLOW.md`，集中记录教学顺序、用户先写代码流程、每日收口门禁和加固周教学边界。
- 更新 `docs/15_MEMORY_SYSTEM.md`，把记忆边界明确为仓库协作记忆、Codex 外部记忆和未来产品运行时记忆三层。
- 更新 `docs/CODEX_PROJECT_BRIEF.md`，把教学模板指向新的教学工作流文档，并明确结束时要给出验证结果和 `Next Required Input`。
- 更新 `DOC_RULES.md`，补充教学流程文档角色和更通用的反漂移检查命令。
- 更新 `docs/INDEX.md`，加入 `docs/16_TEACHING_WORKFLOW.md` 导航。

### 验证

- 本次只修改 Markdown 文档，未修改业务源码。
- Week 6 Day 1 状态未推进，仍为待开始。

### Week 5 Day 7 面试归档与 Week 6 交接

### 本次完成

- 按用户明确确认，将 Week 5 Day 7 三道参考答案作为用户回答。
- 将 Week 5 Day 7 面试题追加到 `docs/Compilation-of-Interview-Questions.md` 的第 36 天记录。
- 确认 Week 5 Day 7 面试题已回答并归档，Week 5 Workspace / Sandbox / Checkpoint 收口。
- 将活跃任务推进到 Week 6 Day 1：Tool Runtime 加固周现状评估。
- 将 Week 5 Day 6-Day 7 活跃实现记录归档到 `docs/archive/implementation_log/2026-07-04-week5-day6-day7-closeout.md`。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 验证

- 本次只修改 Markdown 文档，未修改业务源码。
- Week 5 Day 7 面试题已归档，可以进入 Week 6 Day 1。

### 下一步

- 开始 Week 6 Day 1：按 9 个工业级维度评估 Week 4-5 permission、workspace、checkpoint、runtime 和 rollback 当前差距。
