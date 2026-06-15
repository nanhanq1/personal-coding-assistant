# Implementation Log

## 2026-06-15

### 路线校准：从 Demo 导向修正为工业级项目导向

### 本次完成

- 根据用户要求，明确 12 周路线的最终目标是工业级 Personal Coding Assistant Agent 项目，不是 Demo。
- 更新 `docs/01_LEARNING_ROADMAP.md`：新增路线定位、工业级验收标准、当前路线状态、第 2 周目标状态、第 3 周目标和最终工业级完成定义。
- 更新 `docs/CODEX_PROJECT_BRIEF.md`：将每日任务的“最小验收标准”升级为“工业级验收标准”，并补充每日任务不能只以 Demo 跑通作为验收。
- 更新 `docs/03_WEEKLY_SPRINTS.md`：新增 Sprint 共同原则、第 1/2 周工业级验收标准，并补充第 3 周 Permission System Sprint。
- 更新 `README.md`：明确“最小实现”只是可验证垂直切片，不代表最终质量停留在 Demo。
- 更新 `docs/02_DAILY_TASKS.md`：记录本次路线校准任务。

### 架构决策

- 本次不新增 ADR。
- 本次是项目目标和路线验收标准校准，不改变当前源码架构。

### 验证

- 本次只修改 Markdown 文档，未修改业务代码。
- 已确认后续路线仍从第 3 周 Day 1 Permission System 起步，不改变当前 `docs/09_NEXT_ACTIONS.md` 的课程入口。

## 2026-06-15

### 已完成主线架构与工业级差异整理

### 本次完成

- 新增 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`，专门整理第 1 周 Day 1 到第 2 周 Day 7 的已完成主线。
- 在新文档中明确当前真实主链范围，只覆盖 `src/pca/core`、`src/pca/tools` 和 `src/pca/runtime`。
- 按任务块整理工业级问题总表，覆盖最小 Agent Loop、Tool / ToolRegistry、文件工具、ShellRuntime、工业级加固、Loop + Tools 整合、Week 2 tool schema、`edit_file`、`ToolResult`、结果序列化边界和 `run_command.env` 输出脱敏。
- 为当前真实主链补充整体架构图。
- 为六个模块分别补充高层流程图、细节图和“与工业级项目相比的差异”。
- 单列 `context`、`permissions`、`mcp`、`memory`、`observability` 为占位/计划模块，避免把未来结构误写成已实现能力。
- 同步更新 `docs/02_DAILY_TASKS.md` 和 `docs/09_NEXT_ACTIONS.md`，保持收尾文档一致。

### 架构决策

- 本次不新增 ADR。
- 本次是“已实现主线澄清”和“工业级差异整理”，不改变现有主链架构。

### 验证

- 已用当前仓库证据交叉核对：`docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/06_ARCHITECTURE_DECISIONS.md`、`README.md`、`src/pca/core`、`src/pca/tools`、`src/pca/runtime`。
- 已确认整体架构图中的每个节点都能在当前代码或文档中找到对应落点。
- 已确认占位目录没有被写成已实现能力。
- 已确认表格、整体架构图和模块图统一使用 `ToolRegistry.run(...)`、`ToolResult`、`workspace_root`、`AgentLoop._tool_result_to_message(...)` 等当前真实名称。

