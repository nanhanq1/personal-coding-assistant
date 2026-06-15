# Weekly Sprints

## Sprint 共同原则

本项目最终目标是工业级 Personal Coding Assistant Agent，不是 Demo。每周 Sprint 都必须遵守：

- 每周实现一个可验证的系统能力切片。
- 每周至少覆盖一个关键失败路径或安全边界。
- 每周更新测试、学习笔记、实现日志、下一步行动和面试题归档。
- 每周复盘不仅问“能不能跑”，还要问“距离工业级还缺什么，后续哪一周补”。
- 早期的“最小实现”只是降低单日学习粒度，不代表最终质量标准。

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

### 4.1 本周工业级验收标准

- Agent Loop 有明确 `max_turns` 边界。
- Message / ToolCall 有基础结构校验。
- 工具错误能写回 message history，而不是让主循环无声失败。
- 示例和测试能证明 `tool_call -> tool_result -> final_answer` 闭环。
- 文档必须说明当前仍缺真实 LLM adapter、权限系统、上下文工程和可观测性。

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

### 4.1 本周工业级验收标准

- 默认工具注册表必须是工具事实源，schema 示例不能手写漂移。
- 工具参数必须在 `Tool.run(...)` 统一做第一层基础校验。
- 文件工具和 shell runtime 必须保留 `workspace_root` 等安全边界。
- `edit_file` 必须拒绝空 `old_text`、未命中和多处命中。
- `ToolRegistry.run(...)` 必须返回结构化 `ToolResult`，而不是只靠字符串或异常。
- AgentLoop 必须有明确的 `ToolResult -> tool Message` 序列化边界。
- 本周结束时必须明确：Tool System 只解决“怎么调用工具”，不替代 Permission System。

### 5. 本周复盘问题

- 工具 schema 和工具 handler 的职责边界是什么？
- 参数校验应该放在 `Tool`、具体工具，还是两者都要有？
- `edit_file` 为什么比 `write_file` 更适合 Coding Agent？
- 工具结果为什么需要结构化，而不是全部转成字符串？
- 第 2 周结束后，工具系统距离权限系统还差什么？

## 第 3 周 Sprint

周次：第 3 周
主题：Permission System
总目标：建立执行前风险分类、权限策略、人工审批和审计日志骨架，让 Agent 从“能执行工具”升级为“能判断是否允许执行工具”。

### 1. 本周要掌握的架构能力

- 风险分类：safe / needs_approval / blocked
- 权限策略：allow / ask / deny
- 人工审批流：请求、批准、拒绝、记录
- 命令与文件操作的风险边界
- 审计日志与 trace 入口
- Permission System 和 Tool System 的职责边界

### 2. 本周要实现的核心代码

- `src/pca/permissions/risk.py`：危险命令和危险操作风险分类。
- `src/pca/permissions/policy.py`：最小权限策略判断。
- `src/pca/permissions/approval.py`：审批请求和审批结果数据结构。
- `tests/test_permissions.py` 或拆分测试：覆盖安全命令、需要审批命令、禁止命令、审批通过/拒绝。
- 后续集成点：把策略结果接入 `run_command` 或 AgentLoop 工具执行链路。

### 3. 本周每日安排

| Day | 学习目标 | 代码目标 | 测试目标 | 资料目标 | 复盘目标 |
| --- | --- | --- | --- | --- | --- |
| 1 | 理解危险命令识别 | `CommandRisk` / `RiskLevel` | safe / needs_approval / blocked 分类测试 | shell 安全、Claude Code approval | 能讲清风险分类不是执行拦截 |
| 2 | 理解权限策略 | `PermissionPolicy` | allow / ask / deny 策略测试 | policy engine 基础 | 能讲清策略和风险分类的区别 |
| 3 | 理解人工审批流 | `ApprovalRequest` / `ApprovalDecision` | 批准、拒绝、缺失审批测试 | human-in-the-loop | 能讲清审批为什么是执行前控制 |
| 4 | 接入 run_command 前置检查 | shell 工具执行前检查 | 危险命令不会直接执行 | sandbox / audit | 能讲清工具执行链路如何插入权限 |
| 5 | 文件操作权限边界 | 写文件 / edit_file 风险分类 | 覆盖写入、删除、越界相关策略 | 文件安全 | 能讲清文件工具权限和 workspace 的区别 |
| 6 | 审计日志雏形 | audit event 结构 | 审批与执行记录测试 | observability primer | 能讲清 audit log 和普通日志的区别 |
| 7 | 周复盘和加固 | 收口风险规则和文档 | 全量测试、示例、编译 | 补资料 | 能讲清 Permission System 总链路 |

### 4. 本周最终交付物

- 最小风险分类器。
- 最小权限策略。
- 人工审批数据结构和审批结果语义。
- `run_command` 执行前权限检查的初步集成。
- 审计日志雏形。
- 第 3 周 Permission System 学习笔记、架构图和面试题归档。

### 4.1 本周工业级验收标准

- 危险命令必须在执行前被识别，不能只在执行后记录失败。
- 风险分类必须返回结构化结果，包含等级和理由。
- 策略判断必须可测试、可替换，不硬编码在 `ShellRuntime` 里。
- 审批结果必须可记录，后续能进入审计日志。
- 对“拒绝执行”和“需要审批但未审批”必须有稳定错误语义。
- 文档必须明确当前仍缺完整 sandbox、rollback、进程树治理和企业级策略配置。

### 5. 本周复盘问题

- Permission System 和 Tool System 的边界是什么？
- 为什么危险命令分类必须发生在执行前？
- `safe`、`needs_approval`、`blocked` 三类分别适合什么场景？
- 人工审批结果应该如何进入工具轨迹和审计日志？
- 第 3 周结束后，距离工业级 sandbox / runtime 还差什么？

