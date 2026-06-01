# Daily Tasks

## 2026-06-01

日期：2026-06-01  
当前阶段：第 1 周 Tool System  
当前模块：Day 2 Tool 抽象与 ToolRegistry  
预计用时：1-1.5 小时

### 1. 今日学习目标

- 理解为什么 Agent 不能长期依赖 `dict[str, callable]` 管理工具。
- 理解 `ToolCall`、`Tool`、`ToolRegistry` 和 `AgentLoop` 的职责边界。
- 实现工具注册、查找、执行和错误处理的最小闭环。
- 把 `AgentLoop` 从直接调用函数升级为通过 `ToolRegistry.run(...)` 执行工具。

### 2. 所需前置知识

- Python `dataclass` 的基本用法。
- `Callable[[dict[str, Any]], Any]` 这种函数类型标注的含义。
- 字典查找、重复 key、`KeyError` 的语义。
- Day 1 的 `ToolCall -> tool_result -> assistant final answer` 调用链。

### 3. 今日必须理解的知识点

- `ToolCall` 是 LLM 发出的结构化调用意图，不是真正执行工具。
- `Tool` 是程序侧对真实工具函数的包装，包含名称、描述和执行入口。
- `ToolRegistry` 是工具系统的路由表，负责注册、查找和执行工具。
- `AgentLoop` 不应该关心具体工具函数，只需要把 `tool_call.name` 和 `tool_call.arguments` 交给 registry。

### 4. 今日代码任务

- 实现 `src/pca/tools/base.py` 的 `Tool` 数据结构。
- 实现 `src/pca/tools/registry.py` 的 `ToolRegistry`。
- 新增 `tests/test_tools.py`，覆盖注册、获取、执行、重复注册和未知工具。
- 更新 `src/pca/core/agent_loop.py`，让 Agent Loop 通过 `ToolRegistry` 执行工具。
- 更新 `examples/01_minimal_agent.py`，保持示例脚本可从仓库根目录直接运行。

### 5. 今日资料推荐

- OpenAI Agents SDK：重点看 Tools 概念，理解工具为什么需要描述和统一执行接口。
- mini-SWE-agent：继续观察它如何把工具执行结果写回 trajectory。
- 视频搜索关键词：`AI agent tool registry Python`、`tool calling agent from scratch`。
- 复习资料：ReAct 论文中 action / observation 的交替结构。

### 6. 今日输出物

- `Tool` 抽象。
- `ToolRegistry`。
- 工具系统单元测试。
- Agent Loop 与 ToolRegistry 的集成测试。
- 可运行示例脚本。
- Day 2 架构决策记录。

### 7. 完成情况

- 已完成 `Tool` 和 `ToolRegistry` 的最小实现。
- 已完成工具注册、查找、执行、重复注册和未知工具的测试。
- 已将 `AgentLoop` 从裸 `dict[str, callable]` 升级为使用 `ToolRegistry`。
- 已修复示例脚本导入顺序，保证 `python examples/01_minimal_agent.py` 可从仓库根目录运行。
- 已运行 `python -m pytest -q`，结果为 `8 passed, 1 warning`。
- 当前 warning 是 `.pytest_cache` 写入权限问题，不影响功能验收。
- 下一次继续项目时进入第 1 周 Day 3：文件工具 `read_file` / `write_file` 入门。

## 2026-05-31

日期：2026-05-31  
当前阶段：第 1 周 Agent Loop -> Tool System 准备  
当前模块：Day 1 学习验收与 Day 2 准备  
预计用时：15 分钟

### 1. 今日学习目标

- 确认用户已经读懂 Day 1 最小 Agent Loop 代码。
- 检查用户是否能用自己的话解释 Agent Loop、Message history、ToolCall、mock LLM 和 max_turns。
- 判断是否可以进入第 1 周 Day 2：Tool System 入门。

### 2. 今日检查结果

- 用户已完成 5 个检查问题。
- Agent Loop 的解释已经抓住核心：`user input -> LLM -> tool_call -> tool_result 写回 message history -> LLM -> final answer`。
- Message history 的理解已经到位：它是 Agent 的短期工作记忆和可回放轨迹。
- ToolCall 与普通函数调用的区别已基本掌握：ToolCall 是 LLM 发出的结构化调用意图，普通函数调用是程序逻辑直接执行。
- mock LLM 的意义已掌握：排除真实 LLM 的随机性、网络和 API 干扰，专注验证 Agent Loop 控制流。
- max_turns 的风险意识已建立：避免幻觉、工具错误或停止条件失败导致无限循环、成本失控和内存增长。

### 3. 完成情况

- Day 1 学习验收通过。
- 已修复核心模块和测试中不规范的 `src.pca...` 导入，统一为标准 `pca...` 导入。
- 已运行 `python -m pytest -q`，结果为 `2 passed, 1 warning`。
- 当前无阻塞。
- 下一次继续项目时进入第 1 周 Day 2：Tool System 入门。

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
- 已补充每日任务必须包含资料推荐、所需知识和网页版视频 / 课程页面的长期要求。

### 3. 完成情况

- 已把“不先给出现成完整代码”的教学方式写入 `AGENTS.md`。
- 已把同样规则写入 `docs/CODEX_PROJECT_BRIEF.md`。
- 已把“新增或修改代码注释默认使用中文”的要求写入项目规则和长期提示词。
- 已把“每日任务增加资料推荐、所需知识、网页版视频 / 课程页面”的要求写入项目规则和长期提示词。
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
