# Daily Tasks

本文件只保留当前活跃任务。历史任务归档在 `docs/archive/daily_tasks/`。完整 24 周每日计划见 `docs/14_24_WEEK_PLAN.md`。

## 2026-06-23

日期：2026-06-23
当前阶段：Week 5 Day 1
当前模块：Workspace / Sandbox / Checkpoint - Workspace 抽象
预计用时：1-2 小时
执行状态：待开始。Week 4 Day 7 面试题已回答并归档。

### 1. 今日学习目标

- 理解 workspace 抽象和普通 path helper 的区别。
- 为后续 checkpoint / rollback / sandbox 建立统一的 workspace 边界对象。
- 明确 Week 5 Day 1 只做 workspace 抽象和迁移计划，不直接实现 checkpoint、rollback 或 Docker sandbox。

### 2. 今日前置知识

- Week 4 已实现 permission gate：`ALLOW / ASK / DENY` 能控制 shell 和文件写盘前路径。
- 当前文件工具已有 `_resolve_workspace_path(...)`，shell runtime 也有 workspace/cwd 校验，但逻辑分散。
- Week 5 要把“路径是否在授权 workspace 内”抽象成可复用对象，为后续 snapshot、checkpoint、rollback 提供统一入口。

### 3. 今日代码任务

候选更新：

- `src/pca/runtime/workspace.py`
- `tests/test_workspace.py`
- 必要时为文件工具和 shell runtime 写迁移计划，不急着大范围改主链。

建议新增能力：

- 定义 `Workspace(root)`。
- 支持把相对路径解析为 workspace 内绝对路径。
- 拒绝越界路径、空 root、不存在 root、文件 root。
- 为后续 checkpoint 提供稳定的 root / path 边界 API。

### 4. 今日测试任务

先写测试再实现：

```powershell
E:\python\Scripts\pytest.exe tests\test_workspace.py -q
```

完成后再跑：

```powershell
E:\python\Scripts\pytest.exe -q
python -m compileall src examples -q
```

### 5. 今日阅读任务

- `docs/03_WEEKLY_SPRINTS.md` 的 Week 5 Day 1。
- `docs/14_24_WEEK_PLAN.md` 的 Week 5。
- 资料推荐：
  - Python `pathlib` 官方文档：https://docs.python.org/3/library/pathlib.html
  - OpenHands runtime / workspace / sandbox 相关文档：https://docs.openhands.dev/
  - 视频/课程关键词：`agent workspace sandbox checkpoint rollback`、`python pathlib safe path resolution`

### 6. 今日文档任务

- 完成后更新 `docs/07_IMPLEMENTATION_LOG.md`。
- 完成后更新 `docs/09_NEXT_ACTIONS.md`。
- 如果确定 workspace 抽象边界，更新 `docs/06_ARCHITECTURE_DECISIONS.md`。

### 7. 今日复盘问题

1. workspace 抽象和 `_resolve_workspace_path(...)` helper 的区别是什么？
2. 为什么 checkpoint/rollback 之前要先统一 workspace 边界？
3. 哪些路径输入必须被拒绝？
4. 如果文件工具和 shell runtime 都有自己的路径校验，会带来什么维护风险？
5. Week 5 Day 1 的完成标准为什么不包含 Docker sandbox？

### 8. 今日完成标准

- `Workspace(root)` 的基础测试通过。
- 路径解析和越界拒绝语义清晰。
- 不破坏现有文件工具、shell runtime 和 permission gate 测试。
- 生成 Day 1 面试题，等待用户回答。
