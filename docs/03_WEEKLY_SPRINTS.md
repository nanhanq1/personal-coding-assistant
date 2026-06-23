# Weekly Sprints

本文件保留活跃 Sprint 入口。完整 24 周计划见 `docs/14_24_WEEK_PLAN.md`。

## Sprint 共同原则

- 每周交付一个可运行、可测试、可验收的能力切片。
- 每周至少覆盖一个失败路径或安全边界。
- 每周更新测试、文档、实现日志、下一步行动和面试题状态。
- 每 2 周实现后安排 1 周工业级加固；加固周不新增大模块。
- 文档不能宣称源码没有实现的能力。

## 当前 Sprint：Week 5 - Workspace / Sandbox / Checkpoint

### 1. 本周主题

为文件和命令副作用建立受控 workspace 生命周期：workspace 抽象、checkpoint、rollback 和 sandbox adapter 雏形。

### 2. 本周工业级目标

- 文件和命令副作用可以在授权 workspace 内被隔离和预览。
- 本地文件状态可以在危险修改前创建 checkpoint。
- 失败或用户撤销时可以 rollback 本地 workspace 文件状态。
- sandbox/runtime 接口先抽象清楚，Docker 依赖不提前变成硬要求。

### 3. 核心概念

- workspace root
- snapshot
- checkpoint
- rollback
- runtime interface
- sandbox adapter

### 4. 参考项目

- OpenHands runtime / sandbox / workspace。
- mini-SWE-agent sandbox / environment。
- Aider git workflow。

### 5. 代码模块

- `src/pca/runtime/workspace.py`
- `src/pca/runtime/checkpoints.py`
- `src/pca/runtime/docker_runtime.py`
- `src/pca/runtime/shell_runtime.py`

### 6. 测试任务

- workspace 路径解析和越界拒绝测试。
- checkpoint create / restore 测试。
- dirty workspace rollback 测试。
- sandbox adapter 不可用时 graceful fallback 测试。
- permission denied / failed edit 后 rollback 集成测试。

### 7. 文档任务

- 更新 `docs/09_NEXT_ACTIONS.md`。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`。
- 新增 workspace / checkpoint / sandbox 取舍 ADR。
- 更新当前能力边界，不能宣称已有完整 Docker sandbox。
- Week 5 完成后生成面试题。

### 8. 验收标准

```powershell
E:\python\Scripts\pytest.exe -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python examples\03_observed_tool_run.py
python examples\04_permission_agent.py
python -m compileall src examples -q
```

后续新增示例：

```powershell
python examples\05_checkpoint_rollback.py
```

### 9. 常见风险

- 在本机真实项目中误删或覆盖文件。
- 把 checkpoint 误当成能恢复外部网络/API 副作用。
- 过早依赖 Docker，导致没有 Docker 的开发机无法运行测试。
- 文件工具和 shell runtime 各自维护路径规则，导致边界漂移。

### 10. 本周完成后新增能力

受控 workspace 生命周期雏形：路径边界统一、文件修改可创建 checkpoint、本地文件状态可 rollback，并为后续 sandbox/runtime 替换打基础。

## 当前周每日安排

| Day | 学习目标 | 代码任务 | 测试任务 | 文档任务 | 完成标准 |
|---|---|---|---|---|---|
| 1 | Workspace 抽象 | `Workspace(root)`、路径解析统一迁移计划 | resolve/inside tests | ADR 草稿 | workspace 单测通过 |
| 2 | Checkpoint | `FileCheckpoint` 保存文件快照 | create/restore 测试 | 学习笔记 | restore 通过 |
| 3 | Git checkpoint | `GitCheckpoint` 用 diff 记录 | dirty tree 测试 | 决策记录 | diff 测试通过 |
| 4 | Runtime interface | `CommandRuntime` Protocol | fake runtime 测试 | 架构图 | interface 测试通过 |
| 5 | Sandbox adapter | `DockerRuntime` 占位升级为可检测 adapter | docker unavailable graceful 测试 | 说明限制 | graceful pass |
| 6 | Rollback 集成 | permission denied/failed edit 后 rollback | rollback integration test | 实现日志 | 集成通过 |
| 7 | 验收 | `examples/05_checkpoint_rollback.py` | 全量+安全测试 | 面试题 | 示例可运行 |
