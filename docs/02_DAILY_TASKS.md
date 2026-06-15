# Daily Tasks

## 2026-06-15

日期：2026-06-15
当前阶段：项目路线校准
当前模块：从 Demo 导向修正为工业级项目导向
预计用时：30 分钟

### 1. 今日学习目标

- 明确 12 周路线的最终目标是工业级 Personal Coding Assistant Agent 项目，而不是 Demo。
- 保留“每天做小切片”的学习方法，但把小切片定义为工业级系统的可验证垂直切片。
- 为每日任务和每周 Sprint 增加工业级验收标准。
- 明确后续每周都要持续收敛安全、测试、可观测、权限、上下文和恢复能力。

### 2. 所需前置知识

- 当前第 1 周和第 2 周已经完成的主链能力。
- `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md` 中的工业级差异整理。
- 第 3 周 Permission System 的执行前控制目标。

### 3. 今日必须理解的知识点

- Demo 的特点是“能跑通 happy path”；工业级项目必须考虑失败路径、安全边界、权限、审计、可恢复和可观测。
- “最小实现”不是低质量实现，而是为了把一个工业级系统拆成可学习、可测试、可迭代的小切片。
- 每日任务必须说明当前切片在最终工业级系统中的位置，以及后续哪一周继续补齐缺口。

### 4. 今日文档任务

- 更新 `docs/01_LEARNING_ROADMAP.md`，加入路线定位、工业级验收标准、第 2 周完成状态、第 3 周目标和最终完成定义。
- 更新 `docs/CODEX_PROJECT_BRIEF.md`，把每日任务和每周 Sprint 的验收从“最小验收”升级为“工业级验收标准”。
- 更新 `docs/03_WEEKLY_SPRINTS.md`，加入 Sprint 共同原则、第 1/2 周工业级验收标准和第 3 周 Sprint。
- 更新 `README.md`，明确项目目标是工业级项目，不是 Demo。
- 更新 `docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`，记录本次路线校准。

### 5. 今日资料推荐

- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- OpenTelemetry Observability Primer：https://opentelemetry.io/docs/concepts/observability-primer/
- MCP Specification：https://modelcontextprotocol.io/specification/
- LangGraph durable execution 文档：https://docs.langchain.com/oss/python/langgraph/durable-execution

### 6. 今日输出物

- 工业级项目导向的 `docs/01_LEARNING_ROADMAP.md`
- 带工业级验收要求的 `docs/CODEX_PROJECT_BRIEF.md`
- 带第 3 周 Sprint 和工业级验收标准的 `docs/03_WEEKLY_SPRINTS.md`
- 同步后的 README、实现日志和下一步行动

### 7. 当前完成情况

- 已将路线定位明确为“工业级项目”，不是 Demo。
- 已保留小切片学习方式，但明确小切片必须有测试、失败路径、安全边界、文档和工业级差距说明。
- 已在路线中加入最终工业级完成定义。
- 已在 Sprint 中补充第 3 周 Permission System 的完整周计划和工业级验收标准。
- 下一步仍进入第 3 周 Day 1：危险命令识别与最小权限策略。

## 2026-06-15

日期：2026-06-15
当前阶段：主线架构整理
当前模块：已完成主线架构与工业级差异澄清
预计用时：45 分钟

### 1. 今日学习目标

- 把第 1 周 Day 1 到第 2 周 Day 7 的真实已实现主链整理成一份单独文档。
- 区分“当前已实现架构”和“目录已存在但仍是占位/计划模块”。
- 把每日任务中的工业级问题从分散笔记收敛成一张总表。
- 明确当前项目已经解决的是 Tool System 主链，不是完整工业级 Agent 平台。

### 2. 所需前置知识

- `README.md` 中的当前主链架构图。
- `docs/06_ARCHITECTURE_DECISIONS.md` 中 ADR-0003、ADR-0004、ADR-0005、ADR-0006、ADR-0007。
- `src/pca/core`、`src/pca/tools`、`src/pca/runtime` 的当前实现边界。
- `docs/02_DAILY_TASKS.md` 与 `docs/07_IMPLEMENTATION_LOG.md` 中已有的逐日完成记录。

### 3. 今日必须理解的知识点

- 目录存在不等于能力已实现，架构图必须以真实主链为准。
- 当前真实闭环是 `User -> Message history -> mock LLM -> ToolCall -> AgentLoop -> ToolRegistry -> Tool -> FileTool/ShellRuntime -> ToolResult -> tool Message -> LLM`。
- “工业级问题”不是泛泛而谈，而是要和某个已完成任务块直接对应。
- 流程/治理问题应单列说明，不能和功能模块流程图混在一起。

### 4. 今日代码 / 文档任务

- 新建 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`。
- 在新文档中补充整体架构图、模块流程图、细节图和工业级差异说明。
- 按任务块整理自项目开始以来的工业级问题总表。
- 在文档末尾单列 `context`、`permissions`、`mcp`、`memory`、`observability` 的占位状态说明。
- 更新 `docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 5. 今日资料推荐

- Mermaid Flowchart 官方文档：https://mermaid.js.org/syntax/flowchart.html
- Python `dataclasses` 官方文档：https://docs.python.org/3/library/dataclasses.html
- Python `subprocess` 官方文档：https://docs.python.org/3/library/subprocess.html
- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/

### 6. 今日输出物

- `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`
- 已完成主线的工业级问题总表
- 当前真实主链整体架构图
- 六个模块的流程图、细节图和工业级差异说明
- 占位模块现状说明

### 7. 当前完成情况

- 已基于 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/06_ARCHITECTURE_DECISIONS.md`、`README.md` 和当前源码整理证据。
- 已新增 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`，范围限定为第 1 周 Day 1 到第 2 周 Day 7 的已完成主线。
- 已将 `src/pca/context`、`src/pca/permissions`、`src/pca/mcp`、`src/pca/memory`、`src/pca/observability` 单列为占位/计划模块，不混入当前主链图。
- 已按任务块整理工业级问题总表，并补充整体架构图、模块流程图、细节图和工业级差异。
- 下一步仍然进入第 3 周 Day 1：Permission System 起步；本次整理不改变后续课程路由。

