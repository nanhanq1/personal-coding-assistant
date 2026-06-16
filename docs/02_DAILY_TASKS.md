# Daily Tasks

本文件只保留当前活跃任务。历史任务归档在 `docs/archive/daily_tasks/`。完整 24 周每日计划见 `docs/14_24_WEEK_PLAN.md`。

## 2026-06-15

日期：2026-06-15
当前阶段：Week 3 Day 1
当前模块：Agent Core + Tool Runtime 工业级加固准备
预计用时：1-2 小时

### 1. 今日学习目标

- 理解为什么工业级项目必须先做“状态纠偏”，不能在文档不准确时继续新增能力。
- 区分“目录存在”“模块占位”“模块已接入主链”三种状态。
- 明确 Week 3 加固目标：trace、`ToolResult` 元数据、`ToolRegistry` stats、输出截断、文件大小限制、二进制检测。
- 学会把验收标准绑定到当前可运行命令，而不是只写抽象目标。

### 2. 今日代码任务

今天不新增业务源码功能。

需要核对的源码边界：

- `src/pca/core/agent_loop.py`
- `src/pca/core/messages.py`
- `src/pca/tools/base.py`
- `src/pca/tools/registry.py`
- `src/pca/tools/file_tools.py`
- `src/pca/tools/shell_tools.py`
- `src/pca/runtime/shell_runtime.py`
- `src/pca/context/`
- `src/pca/memory/`
- `src/pca/mcp/`
- `src/pca/observability/`
- `src/pca/permissions/`

### 3. 今日阅读任务

- `AGENTS.md`
- `docs/INDEX.md`
- `docs/09_NEXT_ACTIONS.md`
- `docs/00_PROJECT_CONTEXT.md`
- `docs/01_LEARNING_ROADMAP.md`
- `docs/03_WEEKLY_SPRINTS.md`
- `README.md`
- `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`

### 4. 今日测试任务

确认当前真实基线：

```powershell
python -m pytest -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python -m compileall src examples -q
```

### 5. 今日文档任务

- 修正 `docs/INDEX.md` 中路线周期残留描述。
- 确认 `README.md` 没有把占位目录宣传为已实现能力。
- 瘦身 `docs/09_NEXT_ACTIONS.md`，让它只保留当前状态、能力边界和下一步。
- 归档 `docs/07_IMPLEMENTATION_LOG.md` 的 2026-06-15 旧记录。
- 删除根目录纯导航文件，改用 `docs/INDEX.md` 作为唯一导航入口。
- 用 `DOC_RULES.md` 承载文档规则，避免把文档规则误当成状态记忆。
- 更新 `docs/02_DAILY_TASKS.md` 为 Week 3 Day 1 活跃任务。
- 更新 `docs/07_IMPLEMENTATION_LOG.md` 记录状态纠偏结果。
- 更新 `docs/09_NEXT_ACTIONS.md`，记录 Day 1 验证完成，但面试题回答并归档前不推进 Day 2。

### 6. 今日复盘问题

1. 为什么“有文件”不等于“模块已实现”？
2. 为什么 trace 和 stats 应该在 Tool Runtime 边界设计，而不是随手写 `print`？
3. 当前 `ToolResult` 还缺哪些元数据？
4. 输出截断为什么必须让调用方知道内容被截断？
5. 进入 Week 3 Day 2 前，哪些状态必须确认一致？

### 7. 今日完成标准

- README、路线、Next Actions、Daily Tasks 对当前真实状态描述一致。
- 占位模块仍被明确标记为占位或未接入主链。
- 基线验证命令全部通过。
- `docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md` 低于行数上限。
- `docs/09_NEXT_ACTIONS.md` 记录 Day 1 验证完成，但在面试题回答并归档前不推进到 Week 3 Day 2。

### 8. 今日面试题

状态：待用户回答，暂不归档。

#### 概念理解

为什么工业级项目里“目录或文件已经存在”不等于“该模块已经实现”？请结合 `src/pca/observability/` 或 `src/pca/context/` 举例说明。

#### 源码追查

请沿着当前工具调用主链说明一次 `run_command` 调用会经过哪些核心文件和函数，最终结果如何回写到 `message history`。

#### 系统设计

Week 3 要加入 trace、stats、输出截断和文件资源边界。你会把这些能力分别放在哪些层？为什么不应该把可观测性简单写成散落的 `print`？
