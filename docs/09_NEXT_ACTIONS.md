# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 6 已带边界收口并归档第 43 天面试题，当前进入 Week 7 Day 1。
- 当前主题：Repo Scanner / Repo Map - 文件清单入口。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线、Week 3 Agent Core + Tool Runtime 加固验收、Week 4 Permission System、Week 5 Workspace / Sandbox / Checkpoint、Week 6 Tool Runtime 加固周（现状评估、错误分类、RetryPolicy、Audit、安全集、真实验证、trace 透传和放行复盘）。
- 最新聚焦测试：2026-07-10，audit matrix 为 `20 passed`；工具/permission/rollback 回归集为 `69 passed`；shell runtime 为 `25 passed`。
- 最新安全测试：2026-07-10，`E:\python\Scripts\pytest.exe tests\safety -q` 为 `9 passed`。
- 最新全量测试：2026-07-10，`E:\python\Scripts\pytest.exe -q` 为 `206 passed, 1 skipped`；默认 `python -m pytest -q` 缺少 pytest。
- 最新示例：2026-07-10，五个示例均通过；permission 示例如实输出 `audit_auto_wired=true`，checkpoint 示例输出 `restored=true`。
- 最新编译验证：2026-07-10，`python -m compileall src examples -q` 通过且无输出；此前沙箱 `__pycache__` 写权限问题已由批准后的外部验证覆盖。
- 阻塞项：无；Week 7 Day 1 尚未开始实现。
- 最新文档维护：Week 6 Day 7 面试题已归档为第 43 天；Week 7 Day 1 活跃任务、Sprint 和资源已建立；协作记忆治理、真实模块图谱和代码完成度审计已完成，审计提出的代码整改等待用户批准。

## 当前能力边界

已实现：`Message`、`ToolCall`、`TraceContext`、`AgentEvent`、`ScriptedLLM`、`AgentLoop`（run 级 trace 透传）、`Tool`、`ToolParameter`、`ToolRegistry`（工具调用 metadata 透传）、工具统计、`ToolResult`、`ToolErrorCode`、`RetryDecision`、输出截断、文件资源限制、file/shell runtime、risk/policy、approval 对象、`PermissionAuditEvent`、`record_permission_decision(...)`、shell/file gate 自动摘要审计、`Workspace(root)`、checkpoint 与文件局部 rollback。

仍是占位或未接入主链：retry 不自动执行；审批不支持批准后恢复；audit 不含原子事务、远程后端或查询；结构化日志、trace 查询和 P99 统计未实现；`Workspace(root)` 未成为 shell 主链唯一事实源；Git/Docker/网络等副作用未自动 rollback；`context`、`memory`、`mcp`、完整 `observability`、`cli`。

## 下一步行动

开始 Week 7 Day 1：实现 `RepoScanner.scan(root)` 的最小文件清单契约。

## 用户下次应发送

```text
开始 Week 7 Day 1
```
