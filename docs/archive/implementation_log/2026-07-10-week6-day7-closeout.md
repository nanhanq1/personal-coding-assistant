# Week 6 Tool Runtime 加固周（Day 1-Day 7）

本归档承接 `docs/07_IMPLEMENTATION_LOG.md` 的 Week 6 历史证据；面试题仍以 `docs/Compilation-of-Interview-Questions.md` 为准，本文件不改变其归档状态。

## Day 1：Tool Runtime 加固现状评估

### 代码与文档

- 核对 Week 4-5 permission、workspace、checkpoint、runtime 与 rollback 的源码、测试及 ADR-0014 至 ADR-0024。
- 新增 `docs/17_WEEK6_HARDENING_REPORT.md`，按 9 个工业级维度记录现状、证据、差距和 P0/P1/P2 优先级；同步资源库、Daily Tasks、Next Actions 与文档索引。
- 本日只做评估和文档维护，没有修改生产代码。

### 验证、边界与交接

- 全量测试 `168 passed, 1 skipped`；五个示例及 `python -m compileall src examples -q` 通过。
- 评估不代表九维工业级达标；Day 1 面试题经用户明确确认归档为第 37 天，随后进入 Day 2。

## Day 2：Tool Runtime 错误分类

### 代码与文档

- 按 TDD 为 `ToolResult` 增加稳定的 `ToolErrorCode`，覆盖参数错误、未知工具、permission ASK/DENY、runtime、checkpoint 与 rollback 失败，并从 `pca.tools` 导出。
- 保持 `error_type`、`error_message`、`ToolResult.__str__()` 和既有示例 JSON 兼容；新增 ADR-0025，明确本日不实现 retry、audit 自动接入或 sandbox。

### 验证、边界与交接

- `tests/test_tools.py` 为 `38 passed`；permission/rollback 集为 `13 passed`；全量为 `175 passed, 1 skipped`；五个示例、compileall 与 diff check 通过。
- Day 2 面试题经用户明确确认归档为第 38 天，随后进入 Day 3。

## Day 3：Retry / timeout policy

### 代码与文档

- 按 TDD 新增 `pca.tools.retry`，提供 `RetryDecision`、`RetryPolicy.decide(...)` 与 `should_retry(...)`；策略只读取稳定错误码，不解析自然语言错误。
- `RUNTIME_FAILED` 仅是可重试候选，不会自动重复执行工具；permission、参数、未知工具、checkpoint 与 rollback 失败默认不可重试；新增 ADR-0026 记录该边界。

### 验证、边界与交接

- 记录缺少模块的 RED；随后 retry 聚焦测试 `6 passed`、tools + retry `44 passed`、相关回归 `57 passed`、全量 `181 passed, 1 skipped`；五个示例通过，compileall 经批准后在沙箱外通过。
- Day 3 面试题经用户明确确认归档为第 39 天，并修正面试题文档第 36-38 天的顺序漂移与重复记录，随后进入 Day 4。

## Day 4：Audit 完整性

### 代码与文档

- 按 TDD 新增 `record_permission_decision(...)`，只把 `PermissionDecision` 摘要写成 `PermissionAuditEvent` JSONL；shell、`write_file`、`edit_file` gate 覆盖 ALLOW/ASK/DENY。
- ALLOW 审计写入失败时 fail-closed；ASK/DENY 不执行。审计不记录完整命令、文件路径/内容、env、token、secret、stdout 或 stderr；默认写入进程工作目录 `.pca/permission-audit.jsonl`。
- 修复默认审计路径从未验证 `workspace_root` 派生的问题，更新 permission 示例，并新增 ADR-0027 与 Day 4 设计/实施计划。

### 验证、边界与交接

- audit、shell gate、file gate 矩阵分别为 `4 passed`、`7 passed`、`9 passed`，合并为 `20 passed`；工具/permission/rollback 回归 `69 passed`，shell runtime `25 passed`，全量 `190 passed, 1 skipped`。
- 五个示例通过，permission 示例如实输出 `audit_auto_wired=true`；compileall 经批准后在沙箱外通过，diff check 无空白错误。
- `executed` 只表示获准进入副作用路径，不表示副作用成功；Day 4 面试题经用户确认归档为第 40 天，随后进入 Day 5。

## Day 5：Safety suite

### 代码与文档

- 新增 `tests/safety/`，把 shell permission gate、file workspace/risk gate、audit 摘要与 shell 输出脱敏组织为独立安全回归层。
- 用 `RecordingRuntime` 证明 `rm -rf`、`curl`、`python -c` 分别命中 recursive delete、network access、inline code 且未进入 runtime；用临时 sentinel 验证越界路径、覆盖和删除式编辑没有未授权写盘。
- 用本地 Python list-command 验证敏感环境变量只返回 `[REDACTED]`，audit JSONL 不包含敏感值；没有修改风险规则、稳定错误码或生产 runtime 主链。

### 验证、边界与交接

- Safety 为 `9 passed`，全量为 `199 passed, 1 skipped`；五个示例、compileall 与 diff check 通过。
- 未执行真实网络请求、真实删除命令或外部系统操作；ASK 批准后恢复、完整 sandbox 及 shell/Docker/Git 自动 rollback 仍未实现。
- Day 5 面试题经用户授权归档为第 41 天，随后进入 Day 6。

## Day 6：真实安全验证

### 代码与文档

- 新增 `tests/e2e/test_safe_edit_workflow.py`，在 pytest 临时 `demo_repo` 中串联真实 `ReadFileTool`、`EditFileTool`、`ShellCommandTool` 与 `ToolRegistry`，验证“测试失败 -> 局部修复 -> 测试通过”。
- 覆盖 permission ASK 保持文件不变、workspace 外 sentinel 不变、写盘失败后恢复，以及写盘和恢复同时失败时返回 `ROLLBACK_FAILED`；audit 仅断言固定摘要字段。
- 未修改生产工具链，也未把验证宣称为完整 sandbox、审批恢复或 shell/Git/Docker 自动 rollback。

### 验证、边界与交接

- E2E 为 `5 passed`，Safety 为 `9 passed`，全量为 `204 passed, 1 skipped`；五个示例、compileall 与 diff check 通过。
- 验证只使用 pytest 临时目录，不执行真实网络、真实删除或工作区外写盘；trace 尚未自动透传。
- Day 6 面试题经用户明确授权归档为第 42 天，随后进入 Day 7。

## Day 7：放行复盘与 trace 透传修补

## 代码与测试

- 修复 `AgentLoop -> ToolRegistry -> ToolResult` 的 run 级 trace 透传。
- 每次 `ToolCall` 生成独立 `tool_call_id`。
- 聚焦测试 `45 passed`；E2E `5 passed`；Safety `9 passed`；全量 `206 passed, 1 skipped`。
- 五个示例、compileall 和 `git diff --check` 通过。

## 能力边界

trace metadata 已接入主链，但完整结构化 observability 尚未实现。retry orchestration、审批恢复、audit 原子事务/查询、完整 sandbox 和 Git/Docker/网络 rollback 均未接入。

## 归档与交接

- Day 7 面试题已按用户明确授权归档为第 43 天。
- Week 6 允许带边界进入 Week 7 Repo Scanner，不代表九维工业级全部达标。
