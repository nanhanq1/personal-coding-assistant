# Daily Tasks

## 2026-05-27

日期：2026-05-27  
当前阶段：第 1 周 Agent Loop  
当前模块：项目长期教学规则更新  
预计用时：10 分钟

### 1. 今日学习目标

- 明确后续教学采用“先用户实现，再评审，再注释，再参考实现对比”的训练方式。

### 2. 今日输出物

- 已更新项目教学规则。
- 已写入 Codex 长期记忆更新说明。
- 已补充代码注释默认使用中文的长期要求。

### 3. 完成情况

- 已把“不先给出现成完整代码”的教学方式写入 `AGENTS.md`。
- 已把同样规则写入 `docs/CODEX_PROJECT_BRIEF.md`。
- 已把“新增或修改代码注释默认使用中文”的要求写入项目规则和长期提示词。
- 下一次继续项目时，仍从 Tool System 入门开始，但教学方式按新规则执行。

## 2026-05-26

日期：2026-05-26  
当前阶段：第 1 周 Agent Loop  
当前模块：最小 Agent Loop  
预计用时：1.5-2 小时

### 1. 今日学习目标

- 理解 Agent Loop 为什么是 Coding Agent 的最小骨架。
- 理解 message history 如何把用户、助手和工具结果串起来。
- 理解 mock LLM 如何帮助我们先验证架构，而不是过早接入真实 API。
- 理解 tool_call -> tool_result -> continue 的最小闭环。

### 2. 今日核心概念

| 概念 | 一句话解释 | 类比 | 代码位置 |
| --- | --- | --- | --- |
| Message | Agent 和 LLM 之间传递上下文的标准记录 | 聊天记录本 | `src/pca/core/messages.py` |
| ToolCall | LLM 请求程序执行外部能力的结构化指令 | 让助教帮忙查资料的便条 | `src/pca/core/messages.py` |
| Agent Loop | 不断让 LLM 思考、调用工具、读取结果并继续回答的循环 | 学生做题时查资料、修正答案、再提交 | `src/pca/core/agent_loop.py` |

### 3. 今日代码任务

实现：

- `src/pca/core/messages.py`
- `src/pca/core/mock_llm.py`
- `src/pca/core/agent_loop.py`
- `tests/test_agent_loop.py`
- `examples/01_minimal_agent.py`

### 4. 今日最小验收标准

- `python -m pytest -q` 通过。
- 能手动运行 `python examples/01_minimal_agent.py`。
- 能看到 `tool_call -> tool_result -> final_answer` 的完整流程。

### 5. 今日资料推荐

- 官方文档：OpenAI Agents SDK 的 Tools 和 Runner 概念。
- GitHub 源码：mini-SWE-agent 的 agent loop 和 trajectory。
- 视频搜索关键词：`AI Agents from scratch tool calling tutorial`。
- 论文：ReAct，重点读它如何把 Reasoning 和 Acting 交替组织起来。

### 6. 今日输出物

- 最小 Agent Loop 代码。
- 单元测试。
- 学习笔记。
- Agent Loop 流程图。
- 3 个面试题。

### 7. 完成情况

- 已初始化项目文档和 Python 包结构。
- 已用 TDD 写出 `tests/test_agent_loop.py` 并观察到 RED。
- 已实现最小 Agent Loop、message schema、mock LLM。
- 已补充 `tests/test_examples.py`，保证示例脚本能从仓库根目录直接运行。
- 已运行 `python -m pytest -q`，结果为 `2 passed`。
- 已运行 `python examples/01_minimal_agent.py`，看到 `user -> assistant -> tool -> assistant` 完整链路。
