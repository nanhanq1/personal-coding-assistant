# Weekly Sprints

本文件保留活跃 Sprint 入口。完整 24 周计划见 `docs/14_24_WEEK_PLAN.md`。

## Sprint 共同原则

- 每周交付一个可运行、可测试、可验收的能力切片。
- 每周至少覆盖一个失败路径或安全边界。
- 每周更新测试、文档、实现日志、下一步行动和面试题状态。
- 每 2 周实现后安排 1 周工业级加固；加固周不新增大模块。
- 文档不能宣称源码没有实现的能力。

## 当前 Sprint：Week 6 - Tool Runtime 加固周

当前进度：Week 5 已完成并归档 Day 7 面试题；当前推进 Week 6 Day 1 现状评估。

### 1. 本周主题

将 Week 4-5 的 permission、workspace、checkpoint、runtime 和 rollback 做到可解释、可测、可审计。

### 2. 本周工业级目标

- 按 9 个工业级维度评估当前真实状态。
- 优先补 P0 缺口：安全性、健壮性、可观测性。
- 建立 safety regression matrix 和真实小 repo 安全验证报告。
- 不新增大模块；只加固已有工具运行时、安全边界和文档真实性。

### 3. 核心概念

- error taxonomy
- retry / timeout
- audit completeness
- safety regression
- resource caps
- real-world validation

### 4. 参考项目

- OpenHands evaluation / runtime。
- Cline approval UX。
- mini-SWE-agent environment / trajectory。

### 5. 代码模块

- `src/pca/permissions/*`
- `src/pca/runtime/*`
- `src/pca/tools/*`

### 6. 测试任务

- 基线全量测试和示例。
- error code 测试。
- retry policy 单元测试。
- audit matrix test。
- `tests/safety/` 安全回归测试。
- 真实小 repo safe task 验证。

### 7. 文档任务

- Week 6 加固报告。
- `docs/07_IMPLEMENTATION_LOG.md`。
- `docs/09_NEXT_ACTIONS.md`。
- 必要时更新 `EVALUATION.md`、学习笔记和 ADR。

### 8. 验收标准

```powershell
E:\python\Scripts\pytest.exe -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python examples\03_observed_tool_run.py
python examples\04_permission_agent.py
python examples\05_checkpoint_rollback.py
python -m compileall src examples -q
```

Week 6 后续新增 safety suite 后，必须追加：

```powershell
E:\python\Scripts\pytest.exe tests\safety -q
```

### 9. 常见风险

- 加固时顺手新增大模块，导致边界继续膨胀。
- 只写报告不补测试，无法证明加固有效。
- audit 记录完整命令、文件内容或 secret，造成二次泄漏。
- retry 重试不可重试的危险副作用。
- 把 Docker adapter 误写成完整 sandbox。

### 10. 本周完成后新增能力

安全执行基础达到阶段标准：已有 permission/runtime/checkpoint 能力有清晰错误语义、安全回归测试、audit 完整性检查和真实验证报告。

## 当前周每日安排

| Day | 学习目标 | 代码任务 | 测试任务 | 文档任务 | 完成标准 |
|---|---|---|---|---|---|
| 1 | 现状评估 | 不写功能，列 9 维差距 | 基线测试 | 加固报告初版 | 差距清单完成 |
| 2 | 错误分类 | `ToolErrorCode`、permission error code | error code 测试 | ADR 更新 | 测试通过 |
| 3 | Retry/timeout | 对临时失败定义 retry policy | retry unit tests | 学习笔记 | 测试通过 |
| 4 | Audit 完整性 | audit 覆盖 file/shell/git/memory placeholder | audit matrix test | 更新 EVALUATION | matrix 通过 |
| 5 | Safety suite | 新建 `tests/safety/` | rm/curl/outside/secret cases | 安全报告 | safety 通过 |
| 6 | 真实验证 | 构造 `tmp/demo_repo` 修改任务 | e2e safe task | 真实验证报告 | 报告完成 |
| 7 | 放行复盘 | 修缺口 | 全量+compileall | 面试题 | 阶段放行 |
