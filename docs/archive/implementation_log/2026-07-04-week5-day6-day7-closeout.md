# 2026-07-04 Week 5 Day 6-Day 7 Closeout

本文件归档 Week 5 Day 6 rollback 集成、Day 6 面试归档、Day 7 rollback 验收示例和 Day 7 面试归档的活跃实现记录摘要。当前 live state 以 `docs/09_NEXT_ACTIONS.md` 为准。

## Week 5 Day 6 rollback 集成

- 按 TDD 新增 `tests/test_rollback_integration.py`。
- 在 `WriteFileTool` / `EditFileTool` 的 `DecisionAction.ALLOW` 路径接入 `FileCheckpoint`。
- 写盘失败时调用 `checkpoint.restore()` 恢复本地 workspace 文件状态，再继续抛出原始异常。
- 明确 `ASK` 和 `DENY` 在写盘前阻断，不创建 checkpoint。
- 更新 `examples/04_permission_agent.py` 能力边界：`file_tool_rollback_on_allowed_failure=True`，但 `rollback_auto_wired=False`。
- 新增 ADR-0024，记录 Day 6 rollback 集成边界。

## Week 5 Day 6 面试归档与 Day 7 交接

- 按用户确认，将 Week 5 Day 6 三道参考答案作为用户回答。
- 将 Week 5 Day 6 面试题追加到 `docs/Compilation-of-Interview-Questions.md` 的第 35 天记录。
- 将活跃任务推进到 Week 5 Day 7：本周验收与 rollback 示例。

## Week 5 Day 7 rollback 验收示例

- 按 TDD 在 `tests/test_examples.py` 新增 `test_checkpoint_rollback_example_reports_restored_file_state_and_boundaries`。
- RED：`examples/05_checkpoint_rollback.py` 缺失导致新增测试失败。
- 新增 `examples/05_checkpoint_rollback.py`，用临时 workspace 展示本地文件 checkpoint、模拟失败修改、`FileCheckpoint.restore()` 恢复文件状态。
- 示例输出稳定 JSON，包含原始内容、失败期间临时内容、rollback 后内容和 `restored=True`。
- 示例明确能力边界：只承诺恢复 workspace 内显式跟踪的本地文件状态，不承诺恢复网络/API、包安装、后台进程、workspace 外副作用或 shell/Docker/Git 自动 rollback。

## Week 5 Day 7 验证

- `E:\python\Scripts\pytest.exe tests\test_examples.py::test_checkpoint_rollback_example_reports_restored_file_state_and_boundaries -q`：先 RED，最终 `1 passed`。
- `E:\python\Scripts\pytest.exe tests\test_examples.py -q`：`5 passed`。
- `E:\python\Scripts\pytest.exe -q`：`168 passed, 1 skipped`。
- `python examples\01_minimal_agent.py`：通过。
- `python examples\02_tool_agent.py`：通过。
- `python examples\03_observed_tool_run.py`：通过。
- `python examples\04_permission_agent.py`：通过。
- `python examples\05_checkpoint_rollback.py`：通过，输出 `restored=true` 且不可恢复边界均为 `false`。
- `python -m compileall src examples -q`：2026-07-04 用户在本机 PowerShell 运行后无错误输出，返回提示符，视为通过。

## Week 5 Day 7 面试归档与 Week 6 交接

- 用户明确确认“直接将答案作为用户的回答”。
- 将 Week 5 Day 7 三道参考答案作为用户回答，追加到 `docs/Compilation-of-Interview-Questions.md` 的第 36 天记录。
- Week 5 收口完成，活跃任务推进到 Week 6 Day 1：Tool Runtime 加固周现状评估。
