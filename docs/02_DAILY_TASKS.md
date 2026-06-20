# Daily Tasks

本文件只保留当前活跃任务。历史任务归档在 `docs/archive/daily_tasks/`。完整 24 周每日计划见 `docs/14_24_WEEK_PLAN.md`。

## 2026-06-20

日期：2026-06-20
当前阶段：Week 4 Day 1
当前模块：Permission System - 风险分类
预计用时：1-2 小时
执行状态：待开始。

### 1. 今日学习目标

- 理解 Permission System 解决的是工具执行前控制，不是执行后脱敏或错误包装。
- 建立最小风险等级模型，用于区分安全、需要询问、直接拒绝的命令。
- 明确风险分类和真正拦截执行之间的边界。

### 2. 今日前置知识

- `ShellCommandTool` / `ShellRuntime.run(...)` 当前会直接执行命令。
- `ToolRegistry.run(...)` 当前只负责路由、结果包装、输出截断和 stats。
- Week 3 的 stats、trace 字段和资源限制仍不是权限系统。

### 3. 今日代码任务

更新：

- `src/pca/permissions/risk.py`
- `tests/test_permissions_risk.py`

建议新增能力：

- `RiskLevel`：例如 `SAFE`、`ASK`、`DENY`。
- `RiskAssessment`：保存风险等级、原因和匹配到的规则。
- `classify_command(command)`：先做最小命令风险分类，不接入执行链。

### 4. 今日测试任务

先写失败测试，再实现：

```powershell
E:\python\Scripts\pytest.exe tests\test_permissions_risk.py -q
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

- `docs/14_24_WEEK_PLAN.md` 的 Week 4。
- Cline approval / OpenHands action security 的权限模型，只学习分类思路，不直接照搬实现。

### 6. 今日文档任务

- 更新 `docs/07_IMPLEMENTATION_LOG.md` 记录 Day 7 面试归档和 Day 1 启动。
- 更新 `docs/09_NEXT_ACTIONS.md`，把下一步指向 Week 4 Day 1。
- 如产生架构选择，更新 `docs/06_ARCHITECTURE_DECISIONS.md`。

### 7. 今日复盘问题

1. 风险分类和权限拦截有什么区别？
2. 为什么 Day 1 只做 `classify_command(...)`，不立刻阻止 `run_command`？
3. 字符串规则分类有哪些误判风险？
4. 哪些命令应该直接 `DENY`，哪些应该 `ASK`？
5. 风险分类结果未来如何进入 `PermissionPolicy.decide(...)`？

### 8. 今日完成标准

- 风险分类模型有单元测试覆盖。
- `risk.py` 不再是占位模块。
- 当前实现不提前接入 `ShellRuntime` 或 `ToolRegistry`。
- 全量测试、三个示例和编译验证通过。

### 9. 今日面试题

状态：Day 1 完成后生成。
