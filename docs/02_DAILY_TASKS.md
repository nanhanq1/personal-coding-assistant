# Daily Tasks

本文件只保留当前活跃任务。历史任务归档在 `docs/archive/daily_tasks/`。完整 24 周每日计划见 `docs/14_24_WEEK_PLAN.md`。

## 2026-07-04

日期：2026-07-04
当前阶段：Week 6 Day 1
当前模块：Tool Runtime 加固周 - 现状评估
预计用时：1-2 小时
执行状态：待开始。Week 5 Day 7 面试题已按用户确认归档，Week 5 已收口。2026-07-04 已补充教学协作流程与记忆边界文档，不改变 Week 6 Day 1 任务状态。

### 1. 今日学习目标

- 按 `docs/INDUSTRIAL_STANDARDS.md` 的 9 个维度评估 Week 4-5 的 permission、workspace、checkpoint、runtime 和 rollback 当前状态。
- 区分“已实现能力”“部分达标能力”和“仍未接入主链的工业级缺口”。
- 产出 Week 6 加固报告初版，为后续 Day 2-Day 7 的加固顺序排序。

### 2. 今日前置知识

- Week 4 已完成风险分类、策略判断、审批对象、shell/file gate 和独立 audit 事件。
- Week 5 已完成 `Workspace(root)`、`FileCheckpoint`、`GitCheckpoint`、`CommandRuntime`、`DockerRuntime` graceful fallback、文件工具允许执行失败 rollback 和 Day 7 rollback 验收示例。
- Week 6 是加固周，不新增大模块，先用 9 维标准找差距。

### 3. 今日代码任务

- 不写新功能代码。
- 如评估需要，可新增或更新文档型加固报告。
- 不改变 shell/file/runtime 主链行为。

### 4. 今日测试任务

```powershell
E:\python\Scripts\pytest.exe -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python examples\03_observed_tool_run.py
python examples\04_permission_agent.py
python examples\05_checkpoint_rollback.py
python -m compileall src examples -q
```

### 5. 今日阅读任务

- `docs/INDUSTRIAL_STANDARDS.md`
- `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`
- `ARCHITECTURE.md`
- `docs/06_ARCHITECTURE_DECISIONS.md` 中 ADR-0014 到 ADR-0024

### 6. 今日文档任务

- 建立或更新 Week 6 加固报告初版。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`。
- 更新 `docs/09_NEXT_ACTIONS.md`。
- 必要时更新 `docs/05_LEARNING_NOTES.md`，记录 9 维差距和优先级。

### 附：本次文档维护

- 新增 `docs/16_TEACHING_WORKFLOW.md`，固化教学顺序、用户先写代码流程和每日收口门禁。
- 更新 `docs/15_MEMORY_SYSTEM.md`，明确仓库协作记忆、Codex 外部记忆和未来运行时记忆三层边界。
- 更新 `docs/CODEX_PROJECT_BRIEF.md`、`DOC_RULES.md` 和 `docs/INDEX.md`，减少教学流程和记忆规则分散。

### 7. 今日复盘问题

1. Week 4-5 当前在哪些维度已经部分达标？
2. 哪些缺口属于 P0：安全性、健壮性、可观测性？
3. 哪些能力不能在 Week 6 继续跳过，否则会影响进入 Week 7 Coding Agent？
4. 为什么加固周不应该新增大模块？
5. 如何用测试和真实验证证明加固不是文档口号？

### 8. 今日完成标准

- Week 6 加固报告初版完成。
- 9 个维度都有当前状态、差距和优先级。
- 不新增大模块，不夸大当前能力。
- 基线测试、示例和编译验证有记录。
