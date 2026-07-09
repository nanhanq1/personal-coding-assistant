# 2026-07-01 Week 5 Day 3-Day 4 Runtime / Checkpoint 归档

本文件归档 `docs/07_IMPLEMENTATION_LOG.md` 中已不再属于当前活跃任务的 Week 5 Day 3-Day 4 记录摘要。活跃状态以 `docs/09_NEXT_ACTIONS.md` 为准。

## Week 5 Day 3 GitCheckpoint diff 快照

- 按 TDD 新增 `tests/test_git_checkpoints.py`。
- RED：`GitCheckpoint` 缺失导致 4 个 Day 3 行为测试失败。
- 在 `src/pca/runtime/checkpoints.py` 中新增独立 `GitCheckpoint` API。
- `GitCheckpoint.create(workspace)` 保存 `git diff --binary -- .`，表示 tracked working tree 相对 index 的 dirty diff。
- `checkpoint.restore()` 先执行 `git restore --worktree -- .`，再通过 `git apply --whitespace=nowarn -` 应用保存的 diff。
- 覆盖非 git workspace 的 `ValueError` 和 git 命令不可用的 `RuntimeError`。
- 更新 `examples/04_permission_agent.py` 能力边界：`git_checkpoint_api=True`，但自动 checkpoint/rollback 仍为 `False`。
- 新增 ADR-0021，并同步活跃任务、学习笔记、Sprint、架构状态和下一步门禁。
- 验证：`tests/test_git_checkpoints.py -q` 最终 `4 passed`；相关 checkpoint/workspace 测试 `18 passed`；全量测试当时为 `156 passed, 1 skipped`；四个示例通过；`compileall` 外部权限复跑通过。

## Week 5 Day 3 面试归档与 Day 4 交接

- 按用户确认，将上一轮给出的 Week 5 Day 3 三道参考答案作为用户回答。
- 将 Week 5 Day 3 面试题追加到 `docs/Compilation-of-Interview-Questions.md` 的第 32 天记录。
- 确认 Week 5 Day 3 面试题已回答并归档，`GitCheckpoint` 收口。
- 将活跃任务推进到 Week 5 Day 4：`CommandRuntime` / runtime interface。
- 同步 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/04_RESOURCE_LIBRARY.md`、`docs/09_NEXT_ACTIONS.md` 和 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`。

## Week 5 Day 4 CommandRuntime runtime interface

- 按 TDD 新增 `tests/test_runtime_interface.py`。
- RED：`pca.runtime.interface` 不存在导致 `CommandRuntime` 协议测试失败。
- 新增 `src/pca/runtime/interface.py`，定义最小 `CommandRuntime` Protocol。
- `CommandRuntime.run(arguments)` 保持当前命令结果语义：返回 `stdout`、`stderr`、`returncode`、`timed_out` 等结构化字段。
- 将 `ShellCommandTool` 的 runtime 注入类型从具体 `ShellRuntime` 改为 `CommandRuntime`，默认实现仍为 `ShellRuntime()`。
- 用 fake runtime 测试证明调用方只依赖 `run(arguments)` 接口。
- 更新 `examples/04_permission_agent.py` 能力边界：`command_runtime_interface=True`，但 `sandbox=False`、`checkpoint_auto_wired=False`、`rollback_auto_wired=False`。
- 新增 ADR-0022，并同步活跃任务、学习笔记、Sprint、架构状态和下一步门禁。
- 验证：`tests/test_runtime_interface.py -q` 最终 `3 passed`；权限 shell gate + shell runtime 测试 `28 passed`；Week 5 runtime/checkpoint 相关测试 `21 passed`；全量测试当时为 `159 passed, 1 skipped`；四个示例通过；`compileall` 外部权限复跑通过。

## Week 5 Day 4 面试归档与 Day 5 交接

- 按用户确认，将 Week 5 Day 4 三道参考答案作为用户回答。
- 将 Week 5 Day 4 面试题追加到 `docs/Compilation-of-Interview-Questions.md` 的第 33 天记录。
- 确认 Week 5 Day 4 面试题已回答并归档，`CommandRuntime` interface 收口。
- 将活跃任务推进到 Week 5 Day 5：Docker sandbox adapter graceful fallback。
- 同步 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/05_LEARNING_NOTES.md`、`docs/06_ARCHITECTURE_DECISIONS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md` 和面试题归档。
