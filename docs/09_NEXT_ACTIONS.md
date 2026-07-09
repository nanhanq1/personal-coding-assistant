# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 6 Day 1 等待面试题回答。
- 当前主题：Tool Runtime 加固周 - 现状评估已完成，等待用户回答后归档。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线、Week 3 Agent Core + Tool Runtime 加固验收与 Day 7 面试题归档、Week 4 Permission System 风险分类、策略判断、审批对象、shell gate、文件风险、审计事件、权限验收示例与 Day 7 面试题归档、Week 5 Workspace / Sandbox / Checkpoint 全部 Day 1-Day 7 已完成并归档面试题。
- 最新聚焦测试：2026-07-02，`E:\python\Scripts\pytest.exe tests\test_examples.py::test_checkpoint_rollback_example_reports_restored_file_state_and_boundaries -q` 先 RED 后为 `1 passed`；`E:\python\Scripts\pytest.exe tests\test_examples.py -q` 为 `5 passed`。
- 最新全量测试：2026-07-09，`E:\python\Scripts\pytest.exe -q` 为 `168 passed, 1 skipped`；默认 `python -m pytest -q` 缺少 pytest。
- 最新示例：2026-07-09，`examples\01_minimal_agent.py`、`examples\02_tool_agent.py`、`examples\03_observed_tool_run.py`、`examples\04_permission_agent.py`、`examples\05_checkpoint_rollback.py` 均通过；`examples\05_checkpoint_rollback.py` 输出 `restored=true`。
- 最新编译验证：2026-07-09，`python -m compileall src examples -q` 无错误输出。
- 阻塞项：等待用户回答 Week 6 Day 1 面试题；未回答前不得归档，不得推进 Week 6 Day 2。
- 最新文档维护：2026-07-09 新增 `docs/17_WEEK6_HARDENING_REPORT.md`，并更新 `docs/02_DAILY_TASKS.md`、`docs/04_RESOURCE_LIBRARY.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md` 和 `docs/INDEX.md`。

## 当前能力边界

已实现：`Message`、`ToolCall`、`TraceContext`、`AgentEvent`、`ScriptedLLM`、`AgentLoop`、`Tool`、`ToolParameter`、`ToolRegistry`、`ToolRegistry.get_stats()`、工具调用统计、`ToolResult`、输出截断、文件资源限制、`write_file`、`edit_file`、`run_command` / `ShellRuntime`、`CommandRuntime` Protocol、`DockerRuntime` graceful fallback adapter、`workspace_root`、timeout、env 敏感输出脱敏、`RiskLevel`、`RiskAssessment`、`classify_command(...)`、`classify_file_change(...)`、`PermissionPolicy.decide(...)`、`ApprovalRequest`、`ApprovalDecision`、`PermissionAuditEvent`、`append_audit_event(...)`、shell/file 执行前 permission gate、`Workspace(root)`、`FileCheckpoint`、`GitCheckpoint`、文件工具允许执行失败路径的本地 rollback。

仍是占位或未接入主链：审批对象尚未接入交互式批准流程；shell/file gate 尚未支持审批通过后恢复执行；audit 尚未自动接入 shell/file gate；`Workspace(root)` 尚未迁移接入 shell runtime 主链；`GitCheckpoint` 尚未自动接入失败回滚链路；`GitCheckpoint` 尚不处理 untracked 文件、staged diff、stash、commit 或 sandbox 外副作用；`DockerRuntime` 尚未接入默认主链，尚不是完整 Docker sandbox；shell 命令、Docker、网络/API、包安装、后台进程和 workspace 外副作用尚不支持自动 rollback；`TraceContext` / `AgentEvent` 尚未由 `AgentLoop` 自动创建或透传到 `ToolRegistry`；`context`、`memory`、`mcp`、`observability`、`cli`。

## 下一步行动

开始 Week 6 Day 1：Tool Runtime 加固周现状评估。

### Day 1 任务

1. 阅读 `docs/INDUSTRIAL_STANDARDS.md`。
2. 对 Week 4-5 的 permission、workspace、checkpoint、runtime 和 rollback 做 9 维差距评估。
3. 产出 Week 6 加固报告初版，列出 P0/P1/P2 优先级。
4. 跑基线测试、示例和编译验证。
5. 完成后生成 Week 6 Day 1 面试题，等待用户回答。

## 用户下次应发送

```text
开始 Week 6 Day 1
```
