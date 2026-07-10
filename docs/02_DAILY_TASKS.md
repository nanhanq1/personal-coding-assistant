# Daily Tasks

本文件只保留当前活跃任务。历史任务归档在 `docs/archive/daily_tasks/`。完整 24 周每日计划见 `docs/14_24_WEEK_PLAN.md`。

## 2026-07-10：Week 6 Day 5

日期：2026-07-10
当前阶段：Week 6 Tool Runtime 加固周
当前模块：Safety suite
预计用时：1-2 小时
执行状态：代码、测试和验证已完成；Week 6 Day 5 面试题待生成、回答和归档。Week 6 Day 4 面试题已按用户确认归档为第 40 天记录。

### 1. 今日学习目标

- 把 permission、workspace、audit 的安全边界转成可重复运行的回归测试。
- 覆盖 destructive command、network/inline code、workspace 外路径和 secret redaction。
- 保持 Safety suite 只验证已有行为，不新增大型安全平台或审批恢复流程。

### 2. 今日前置知识

- Week 4 已完成风险分类、策略判断、shell/file gate 和权限审计事件。
- Week 5 已完成 Workspace、checkpoint、rollback 和 runtime 边界。
- Week 6 Day 4 已完成 shell/file gate audit matrix、摘要字段、隐私边界和 fail-closed 测试。

### 3. 今日代码任务

- 新建 `tests/safety/` 测试目录及最小测试配置。
- 将 destructive command、network command、inline code、outside workspace、overwrite/delete-like edit、secret redaction 组织为安全回归用例。
- 每个用例断言：真实副作用是否发生、错误码是否稳定、审计是否存在且不泄漏敏感值。
- 不实现新的风险分类规则；发现缺口时先记录，不在 Day 5 顺手扩张模块。

### 4. 今日测试任务

```powershell
E:\python\Scripts\pytest.exe tests\safety -q
E:\python\Scripts\pytest.exe -q
```

完成后补跑五个示例、`python -m compileall src examples -q` 和 `git diff --check`。

本次实际验证：`tests/safety` 为 `9 passed`；全量为 `199 passed, 1 skipped`；五个示例、compileall 和 diff check 均通过。

### 5. 今日阅读任务

- `docs/INDUSTRIAL_STANDARDS.md`
- `docs/17_WEEK6_HARDENING_REPORT.md`
- `ARCHITECTURE.md`
- `docs/03_WEEKLY_SPRINTS.md` 中 Week 6 Safety suite 约束

### 6. 今日文档任务

- 更新 `docs/07_IMPLEMENTATION_LOG.md`，记录安全回归矩阵和真实失败边界。
- 更新 `docs/09_NEXT_ACTIONS.md` 与 `docs/17_WEEK6_HARDENING_REPORT.md`。
- 如新增安全测试约定，再更新 `EVALUATION.md`。

### 7. 今日复盘问题

1. 安全回归测试与普通 permission 单元测试的边界是什么？
2. 为什么安全测试必须断言“副作用没有发生”，不能只断言异常类型？
3. secret redaction 测试如何避免把 secret 本身写进测试失败输出或审计日志？

### 8. 今日完成标准

- `tests/safety` 已覆盖计划中的危险命令、网络/inline code、越界路径、覆盖/删除式编辑和 secret 脱敏。
- 安全测试与全量测试已通过。
- 失败路径均有稳定错误语义、无未授权副作用、无敏感数据泄漏。
- 已记录真实网络/删除、审批恢复、完整 sandbox 和自动 rollback 等未覆盖边界；下一步生成 Day 5 面试题并等待回答。
