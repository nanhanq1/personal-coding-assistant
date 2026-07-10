# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 6 Day 5 实现已完成，等待面试题回答与归档。
- 当前主题：Tool Runtime 加固周 - Safety suite。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线、Week 3 Agent Core + Tool Runtime 加固验收与 Day 7 面试题归档、Week 4 Permission System、Week 5 Workspace / Sandbox / Checkpoint、Week 6 Day 1 现状评估、Day 2 错误分类、Day 3 RetryPolicy、Day 4 shell/file gate 审计完整性（均已归档面试题），以及 Day 5 Safety suite 实现与验证（面试题待归档）。
- 最新聚焦测试：2026-07-10，audit matrix 为 `20 passed`；工具/permission/rollback 回归集为 `69 passed`；shell runtime 为 `25 passed`。
- 最新安全测试：2026-07-10，`E:\python\Scripts\pytest.exe tests\safety -q` 为 `9 passed`。
- 最新全量测试：2026-07-10，`E:\python\Scripts\pytest.exe -q` 为 `199 passed, 1 skipped`；默认 `python -m pytest -q` 缺少 pytest。
- 最新示例：2026-07-10，五个示例均通过；permission 示例如实输出 `audit_auto_wired=true`，checkpoint 示例输出 `restored=true`。
- 最新编译验证：2026-07-10，沙箱内 `python -m compileall src examples -q` 因 `__pycache__` 写权限失败；批准后外部重跑通过且无输出。
- 阻塞项：Day 5 面试题等待用户回答；代码、测试和验证无阻塞。
- 最新文档维护：Day 5 Safety suite 已同步实现日志、评估约定和加固报告；Day 5 面试题待生成并等待回答。

## 当前能力边界

已实现：`Message`、`ToolCall`、`TraceContext`、`AgentEvent`、`ScriptedLLM`、`AgentLoop`、`Tool`、`ToolParameter`、`ToolRegistry`、工具统计、`ToolResult`、`ToolErrorCode`、`RetryDecision`、输出截断、文件资源限制、file/shell runtime、risk/policy、approval 对象、`PermissionAuditEvent`、`record_permission_decision(...)`、shell/file gate 自动摘要审计、`Workspace(root)`、checkpoint 与文件局部 rollback。

仍是占位或未接入主链：retry 不自动执行；审批不支持批准后恢复；audit 不含原子事务、远程后端、查询或 trace 关联；`Workspace(root)` 未成为 shell 主链唯一事实源；Git/Docker/网络等副作用未自动 rollback；trace 未自动透传；`context`、`memory`、`mcp`、完整 `observability`、`cli`。

## 下一步行动

完成 Week 6 Day 5 的面试题回答、归档和最终文档收口；之后再评估是否进入 Day 6 真实验证。

## 用户下次应发送

```text
回答 Week 6 Day 5 面试题；当前不推进到 Day 6。
```
