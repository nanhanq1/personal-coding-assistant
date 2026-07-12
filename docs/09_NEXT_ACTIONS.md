# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 6 已带边界收口并归档第 43 天面试题，当前进入 Week 7 Day 1。
- 当前主题：Repo Scanner / Repo Map - 文件清单入口。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线、Week 3 Agent Core + Tool Runtime 加固验收、Week 4 Permission System、Week 5 Workspace / Sandbox / Checkpoint、Week 6 Tool Runtime 加固周（现状评估、错误分类、RetryPolicy、Audit、安全集、真实验证、trace 透传和放行复盘）。
- 最新聚焦测试：2026-07-12，tools 为 `48 passed`，approval 为 `21 passed`，tools/approval/retry/AgentLoop 相关回归为 `81 passed`；覆盖非法名称、非法 trace、保留统计键和 DST fold。
- 最新安全测试：2026-07-12，wrapper safety 用例已包含在聚焦与全量回归中，已知 wrapper 不进入 fake runtime。
- 最新全量测试：2026-07-12，`E:\python\Scripts\pytest.exe -q` 为 `243 passed, 1 skipped`。
- 最新示例：2026-07-12，五个示例均通过；permission 示例包含直接安全命令、直接 DENY 和 wrapper ASK 三条路径。
- 最新编译验证：2026-07-12，沙箱内受 `__pycache__` 写权限限制；批准后在沙箱外执行 `E:\python\python.exe -m compileall src examples -q`，退出码为 0。
- 阻塞项：无；Week 7 Day 1 尚未开始实现。
- 最新维护：审计 F-01 P0 与 F-02/F-03 P1 已按批准方案修复并验证；F-04 audit 生命周期与 F-05 工程质量门禁仍需单独设计批准。Week 7 Day 1 尚未开始。

## 当前能力边界

已实现：`Message`、`ToolCall`、`TraceContext`、`AgentEvent`、`ScriptedLLM`、`AgentLoop`（run 级 trace 透传）、`Tool`、`ToolParameter`、`ToolRegistry`（工具调用 metadata 透传）、工具统计、`ToolResult`、`ToolErrorCode`、`RetryDecision`、输出截断、文件资源限制、file/shell runtime、risk/policy、approval 对象、`PermissionAuditEvent`、`record_permission_decision(...)`、shell/file gate 自动摘要审计、`Workspace(root)`、checkpoint 与文件局部 rollback。

已知 `cmd` / `powershell` / `pwsh` wrapper 统一 fail-closed 为 `ASK/shell_wrapper`，不会静默进入 runtime；但尚未解析其内部、嵌套、编码或动态构造的命令语义。

`ToolRegistry.run(...)` 对非法名称或 trace metadata 保持稳定 `INVALID_ARGUMENT` 结果并使用保留的有界统计桶；approval 字符串、bool 和时间字段已有严格错误契约，aware datetime 按 UTC 绝对时刻比较。

仍是占位或未接入主链：retry 不自动执行；审批不支持批准后恢复；audit 不含原子事务、远程后端或查询；结构化日志、trace 查询和 P99 统计未实现；`Workspace(root)` 未成为 shell 主链唯一事实源；Git/Docker/网络等副作用未自动 rollback；`context`、`memory`、`mcp`、完整 `observability`、`cli`。

## 下一步行动

开始 Week 7 Day 1：实现 `RepoScanner.scan(root)` 的最小文件清单契约。

## 用户下次应发送

```text
开始 Week 7 Day 1
```
