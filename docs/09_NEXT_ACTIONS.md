# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 4 Day 1 待开始。
- 当前主题：Permission System - 风险分类。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线、Week 3 Agent Core + Tool Runtime 加固验收与 Day 7 面试题归档。
- 最新测试：2026-06-20 复核，`E:\python\Scripts\pytest.exe -q` 为 `110 passed, 1 skipped`；默认 `python -m pytest -q` 缺少 pytest。
- 最新示例：2026-06-20 复核，`examples\01_minimal_agent.py`、`examples\02_tool_agent.py`、`examples\03_observed_tool_run.py` 均通过。
- 最新编译验证：2026-06-20 复核，`python -m compileall src examples -q` 通过。
- 阻塞项：无；Week 4 Day 1 尚未实现。
- 最新文档维护：Day 7 面试题已归档到 `docs/Compilation-of-Interview-Questions.md` 第 22 天；活跃任务已推进到 Week 4 Day 1。

## 当前能力边界

已实现：`Message`、`ToolCall`、`TraceContext`、`AgentEvent`、`ScriptedLLM`、`AgentLoop`、`Tool`、`ToolParameter`、`ToolRegistry`、`ToolRegistry.get_stats()`、工具调用 `calls/successes/failures/total_duration_ms` 统计、`ToolResult`、`ToolResult.trace_id`、`ToolResult.tool_call_id`、`ToolResult.output_truncated`、`truncate_output(...)`、shell stdout/stderr 截断、字符串 payload 截断、`read_file` 文件大小上限、`read_file` 明显二进制拒绝、`write_file`、`edit_file`、`run_command` / `ShellRuntime`、`workspace_root`、timeout、基础参数校验、`run_command.env` 敏感输出脱敏。

仍是占位或未接入主链：`permissions` 仍未实现；`TraceContext` / `AgentEvent` 尚未由 `AgentLoop` 自动创建或透传到 `ToolRegistry`；`ToolRegistry` stats 尚未接入 logger hook 或持久化 metrics；文件资源限制仍是固定上限和最小 NUL 检测；`context`、`memory`、`mcp`、`observability`、`workspace/checkpoint/docker_runtime`、`cli`。

## 下一步行动

开始 Week 4 Day 1：风险分类。

### Day 1 任务

1. 按 TDD 新增 `tests/test_permissions_risk.py`。
2. 在 `src/pca/permissions/risk.py` 实现 `RiskLevel`、`RiskAssessment` 和 `classify_command(...)`。
3. 只做分类，不接入 `ShellRuntime`、`ShellCommandTool` 或 `ToolRegistry`。
4. 跑聚焦测试、全量测试、三个示例和编译验证。
5. 更新 `docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`；完成后生成 Day 1 面试题。

## 用户下次应发送

```text
开始 Week 4 Day 1
```
