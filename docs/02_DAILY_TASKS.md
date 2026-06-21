# Daily Tasks

本文件只保留当前活跃任务。历史任务归档在 `docs/archive/daily_tasks/`。完整 24 周每日计划见 `docs/14_24_WEEK_PLAN.md`。

## 2026-06-21

日期：2026-06-21
当前阶段：Week 4 Day 2
当前模块：Permission System - 策略判断
预计用时：1-2 小时
执行状态：待开始。

### 1. 今日学习目标

- 理解风险分类只描述命令危险程度，策略判断才决定 allow / ask / deny。
- 建立最小 `PermissionPolicy.decide(...)`，为后续审批对象和 shell gate 做准备。
- 明确 policy 不应该执行命令，也不应该直接写审计日志。

### 2. 今日前置知识

- Week 4 Day 1 已实现 `RiskLevel`、`RiskAssessment` 和 `classify_command(...)`。
- `classify_command(...)` 仍未接入 `ShellRuntime`、`ShellCommandTool` 或 `ToolRegistry`。
- Day 2 只做策略判断，不做人工审批、不接 shell gate。

### 3. 今日代码任务

更新：

- `src/pca/permissions/policy.py`
- `tests/test_permissions_policy.py`

建议新增能力：

- `PermissionDecision`：保存决策结果、原因和风险评估。
- `DecisionAction` 或等价枚举：`ALLOW`、`ASK`、`DENY`。
- `PermissionPolicy.decide(assessment)`：把风险等级映射为策略动作。

### 4. 今日测试任务

先写失败测试，再实现：

```powershell
E:\python\Scripts\pytest.exe tests\test_permissions_policy.py -q
```

完成后再跑：

```powershell
E:\python\Scripts\pytest.exe -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python examples\03_observed_tool_run.py
python -m compileall src examples -q
```

### 5. 今日阅读任务

- `docs/03_WEEKLY_SPRINTS.md` 的 Week 4 Day 2。
- 回看 `docs/06_ARCHITECTURE_DECISIONS.md` 的 ADR-0013，确认分类和策略边界。

### 6. 今日文档任务

- 更新 `docs/07_IMPLEMENTATION_LOG.md` 记录 Day 1 面试归档和 Day 2 启动。
- 更新 `docs/09_NEXT_ACTIONS.md`，把下一步指向 Week 4 Day 2。
- 如产生新的策略边界选择，更新 `docs/06_ARCHITECTURE_DECISIONS.md`。

### 7. 今日复盘问题

1. `RiskLevel` 和 `DecisionAction` 为什么不能混成一个枚举？
2. `PermissionPolicy.decide(...)` 为什么不应该直接调用 `ShellRuntime`？
3. 哪些信息应该进入 `PermissionDecision`，哪些应留给审计事件？
4. 默认策略应该如何处理未知风险或缺失 assessment？
5. Day 2 的策略判断未来如何接入 Day 3 审批对象？

### 8. 今日完成标准

- policy 模型有单元测试覆盖。
- `policy.py` 不再是占位模块。
- 当前实现不提前接入 shell gate 或 audit。
- 全量测试、三个示例和编译验证通过。

### 9. 今日面试题

状态：Day 2 完成后生成。
