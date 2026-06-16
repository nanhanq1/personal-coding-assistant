# Next Actions

本文件是当前状态和下一步的唯一权威源。启动读取顺序见 `AGENTS.md`。

## 当前状态

- 路线阶段：24 周工业级路线，Week 3 Day 1 验证完成。
- 当前主题：Agent Core + Tool Runtime 工业级加固。
- 真实已完成：Week 1 Agent Loop、Week 2 Tool Runtime 基线。
- 最新测试：`python -m pytest -q` 为 `93 passed, 1 skipped`。
- 最新示例：`examples\01_minimal_agent.py`、`examples\02_tool_agent.py` 均通过。
- 最新编译验证：`python -m compileall src examples -q` 通过。
- 阻塞项：Week 3 Day 1 面试题尚未回答，不能归档 Day 1，不能推进 Day 2。
- 最新文档维护：已瘦身文档入口、归档实现日志、删除根目录纯导航文件。

## 当前能力边界

已实现：`Message`、`ToolCall`、`ScriptedLLM`、`AgentLoop`、`Tool`、`ToolParameter`、`ToolRegistry`、`ToolResult`、`read_file`、`write_file`、`edit_file`、`run_command` / `ShellRuntime`、`workspace_root`、timeout、基础参数校验、`run_command.env` 敏感输出脱敏。

仍是占位或未接入主链：`permissions`、`context`、`memory`、`mcp`、`observability`、`workspace/checkpoint/docker_runtime`、`cli`。

详细已实现主线与差距见 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`。

## 下一步行动

先完成 Week 3 Day 1 面试题回答与归档。

### Day 1 面试题

1. 概念理解：为什么工业级项目里“目录或文件已经存在”不等于“该模块已经实现”？请结合 `src/pca/observability/` 或 `src/pca/context/` 举例说明。
2. 源码追查：请沿着当前工具调用主链说明一次 `run_command` 调用会经过哪些核心文件和函数，最终结果如何回写到 `message history`。
3. 系统设计：Week 3 要加入 trace、stats、输出截断和文件资源边界。你会把这些能力分别放在哪些层？为什么不应该把可观测性简单写成散落的 `print`？

## 用户下次应发送

```text
回答 Week 3 Day 1 面试题：...
```
