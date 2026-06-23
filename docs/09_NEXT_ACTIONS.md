# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 5 Day 1 待开始。
- 当前主题：Workspace / Sandbox / Checkpoint - Workspace 抽象。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线、Week 3 Agent Core + Tool Runtime 加固验收与 Day 7 面试题归档、Week 4 Permission System 风险分类、策略判断、审批对象、shell gate、文件风险、审计事件、权限验收示例与 Day 7 面试题归档。
- 最新聚焦测试：2026-06-23，`E:\python\Scripts\pytest.exe tests\test_examples.py -q` 为 `4 passed`。
- 最新全量测试：2026-06-23，`E:\python\Scripts\pytest.exe -q` 为 `138 passed, 1 skipped`；默认 `python -m pytest -q` 缺少 pytest。
- 最新示例：2026-06-23，`examples\01_minimal_agent.py`、`examples\02_tool_agent.py`、`examples\03_observed_tool_run.py`、`examples\04_permission_agent.py` 均通过。
- 最新编译验证：2026-06-23，`python -m compileall src examples -q` 通过。
- 阻塞项：无；Week 5 Day 1 尚未实现。
- 最新文档维护：2026-06-23 归档 Week 4 Day 7 面试题到 `docs/Compilation-of-Interview-Questions.md` 第 29 天，并推进活跃任务到 Week 5 Day 1。

## 当前能力边界

已实现：`Message`、`ToolCall`、`TraceContext`、`AgentEvent`、`ScriptedLLM`、`AgentLoop`、`Tool`、`ToolParameter`、`ToolRegistry`、`ToolRegistry.get_stats()`、工具调用 `calls/successes/failures/total_duration_ms` 统计、`ToolResult`、`ToolResult.trace_id`、`ToolResult.tool_call_id`、`ToolResult.output_truncated`、`truncate_output(...)`、shell stdout/stderr 截断、字符串 payload 截断、`read_file` 文件大小上限、`read_file` 明显二进制拒绝、`write_file`、`edit_file`、`run_command` / `ShellRuntime`、`workspace_root`、timeout、基础参数校验、`run_command.env` 敏感输出脱敏、`RiskLevel`、`RiskAssessment`、`classify_command(...)`、`classify_file_change(...)`、`DecisionAction`、`PermissionDecision`、`PermissionPolicy.decide(...)`、`ApprovalRequest`、`ApprovalDecision`、`PermissionAuditEvent`、`append_audit_event(...)`、`ShellCommandTool` 执行前 shell gate、`WriteFileTool`/`EditFileTool` 写盘前文件风险 gate。

仍是占位或未接入主链：审批对象尚未接入交互式批准流程；shell/file gate 尚未支持审批通过后恢复执行；audit 尚未自动接入 shell/file gate；尚未有统一 `Workspace(root)` 抽象；尚未实现 checkpoint/rollback；尚未实现 Docker sandbox adapter；`TraceContext` / `AgentEvent` 尚未由 `AgentLoop` 自动创建或透传到 `ToolRegistry`；`ToolRegistry` stats 尚未接入 logger hook 或持久化 metrics；文件资源限制仍是固定上限和最小 NUL 检测；`context`、`memory`、`mcp`、`observability`、`cli`。

## 下一步行动

开始 Week 5 Day 1：Workspace 抽象。

### Day 1 任务

1. 按 TDD 新增 `tests/test_workspace.py`。
2. 新增 `src/pca/runtime/workspace.py`，定义 `Workspace(root)`。
3. 覆盖 root 不存在、root 是文件、相对路径解析、绝对路径越界、`..` 越界等测试。
4. 先稳定 API 和迁移计划，不大范围改文件工具和 shell runtime 主链。
5. 完成后跑聚焦测试、全量测试和编译验证；生成 Day 1 面试题。

## 用户下次应发送

```text
开始 Week 5 Day 1
```
