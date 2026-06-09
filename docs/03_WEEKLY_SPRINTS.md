# Weekly Sprints

## 第 1 周 Sprint

周次：第 1 周  
主题：Agent Loop  
总目标：实现最小 Agent 循环，理解 Coding Agent 的执行骨架。

### 1. 本周要掌握的架构能力

- Message history
- LLM adapter mock
- Tool calling
- Tool result 回写
- Loop runner
- 最小测试策略

### 2. 本周要实现的核心代码

- `src/pca/core/messages.py`：消息和工具调用数据结构。
- `src/pca/core/mock_llm.py`：可脚本化 mock LLM。
- `src/pca/core/agent_loop.py`：最小 Agent Loop。
- `tests/test_agent_loop.py`：Agent Loop 行为测试。
- `examples/01_minimal_agent.py`：手动运行示例。

### 3. 本周每日安排

| Day | 学习目标 | 代码目标 | 测试目标 | 资料目标 | 复盘目标 |
| --- | --- | --- | --- | --- | --- |
| 1 | 理解最小 Agent Loop | messages、mock LLM、agent loop | tool_call 闭环测试 | ReAct、mini-SWE-agent loop | 能讲清楚 Agent Loop |
| 2 | 理解 Tool 抽象 | Tool、ToolRegistry | 工具注册和执行测试 | OpenAI Agents SDK Tools | 能讲清工具为什么要注册 |
| 3 | 理解文件工具 | read_file、write_file | 文件读写测试 | Aider file editing | 能讲清输入输出和失败 |
| 4 | 理解 shell runtime 雏形 | run_bash mock / subprocess | 命令执行测试 | mini-SWE-agent environment | 能讲清 runtime 边界 |
| 5 | 整合 Loop + Tools | tool router | 多工具调用测试 | Claude Code tools 思想 | 能讲清路由链路 |
| 6 | 文档和架构图 | README 初稿 | 示例运行 | ReAct 复读和笔记 | 能画出闭环图 |
| 7 | 周复盘 | 小重构 | 全量测试 | 补资料 | 整理面试讲解稿 |

### 4. 本周最终交付物

- 可运行的最小 Agent。
- 单元测试。
- README 说明。
- Agent Loop 架构图。
- 学习笔记。
- 面试讲解稿初稿。

### 5. 本周复盘问题

- 我学会了什么？
- 哪些地方没理解？
- 哪些代码需要重构？
- 哪些设计可以工业级增强？
- 如果面试官问我 Agent Loop，我怎么讲？

## 第 2 周 Sprint

周次：第 2 周  
主题：Tool System 深化  
总目标：把第 1 周的最小工具路由升级成更接近真实 Coding Agent 的工具系统，重点补齐工具参数 schema、局部编辑、结构化结果和错误语义。

### 1. 本周要掌握的架构能力

- 工具参数 schema
- 工具元数据导出
- 工具输入的统一入口校验
- `edit_file` 局部编辑能力
- 结构化 tool result
- 工具错误分类和可恢复语义

### 2. 本周要实现的核心代码

- `src/pca/tools/base.py`：`ToolParameter` 和 `Tool.to_schema()`。
- `src/pca/tools/registry.py`：注册表统一导出工具 schema。
- `src/pca/tools/file_tools.py`：文件工具声明参数 schema。
- `src/pca/tools/shell_tools.py`：shell 工具声明参数 schema。
- 后续：`edit_file`、结构化 tool result、工具执行元数据。

### 3. 本周每日安排

| Day | 学习目标 | 代码目标 | 测试目标 | 资料目标 | 复盘目标 |
| --- | --- | --- | --- | --- | --- |
| 1 | 理解工具 schema 为什么是 LLM 与程序的契约 | ToolParameter、Tool.to_schema、ToolRegistry schema 导出 | schema 导出、必填参数、类型校验 | JSON Schema、OpenAI tool calling | 能讲清 schema 与业务校验的区别 |
| 2 | 理解工具参数 schema 如何服务真实 LLM adapter | 统一内置工具 schema 展示和示例 | 默认工具注册表 schema 测试 | OpenAI / Anthropic tool schema | 能讲清工具描述如何帮助模型选工具 |
| 3 | 理解局部编辑比整文件覆盖更安全 | edit_file 雏形 | 替换文本、未命中、越界、空替换测试 | diff / patch 基础 | 能讲清 edit_file 的风险 |
| 4 | 理解结构化 tool result | ToolResult 数据结构 | 成功、失败、错误类型、耗时测试 | observability 基础 | 能讲清 result 与 message content 的关系 |
| 5 | 整合 schema + edit_file + result | AgentLoop 消费结构化工具结果 | 多工具集成测试 | mini-SWE-agent trajectory | 能讲清完整工具链路 |
| 6 | 文档和面试表达 | 更新 README 和第 2 周讲解稿 | 示例运行 | 官方文档复读 | 能画出第 2 周工具系统图 |
| 7 | 周复盘和小重构 | 修补一个真实边界缺口 | 全量测试 | 补资料 | 整理第 2 周面试讲解 |

### 4. 本周最终交付物

- 工具参数 schema 能力。
- 内置工具 schema 导出。
- `edit_file` 局部编辑工具。
- 结构化 tool result。
- 第 2 周工具系统学习笔记和面试题归档。

### 5. 本周复盘问题

- 工具 schema 和工具 handler 的职责边界是什么？
- 参数校验应该放在 `Tool`、具体工具，还是两者都要有？
- `edit_file` 为什么比 `write_file` 更适合 Coding Agent？
- 工具结果为什么需要结构化，而不是全部转成字符串？
- 第 2 周结束后，工具系统距离权限系统还差什么？

