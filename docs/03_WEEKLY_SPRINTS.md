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

