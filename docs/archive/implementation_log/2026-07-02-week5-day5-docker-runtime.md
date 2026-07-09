# 2026-07-02 Week 5 Day 5 DockerRuntime 归档

本文件归档 `docs/07_IMPLEMENTATION_LOG.md` 中已不再属于当前活跃任务的 Week 5 Day 5 记录摘要。活跃状态以 `docs/09_NEXT_ACTIONS.md` 为准。

## Week 5 Day 5 面试归档与 Day 6 交接

- 按用户确认，将 Week 5 Day 5 三道参考答案作为用户回答。
- 将 Week 5 Day 5 面试题追加到 `docs/Compilation-of-Interview-Questions.md` 的第 34 天记录。
- 确认 Week 5 Day 5 面试题已回答并归档，`DockerRuntime` graceful fallback adapter 可以收口。
- 将活跃任务推进到 Week 5 Day 6：permission denied / failed edit 后 rollback 集成。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

## Week 5 Day 5 DockerRuntime graceful fallback

- 按 TDD 新增 `tests/test_docker_runtime.py`。
- RED：`pca.runtime.docker_runtime` 只有占位说明，缺少 `DockerRuntime`，4 个 Day 5 行为测试失败。
- 将 `src/pca/runtime/docker_runtime.py` 升级为最小 `DockerRuntime` adapter，实现 `CommandRuntime.run(arguments)` 形状。
- Docker CLI 缺失时返回稳定 fallback：`returncode=127`、`sandboxed=False`、`fallback="docker_unavailable"`。
- Docker daemon 不可用时返回稳定 fallback：`returncode=125`、`sandboxed=False`、`fallback="docker_unavailable"`。
- Docker 不可用时不会静默回退到宿主机 shell。
- 更新 `examples/04_permission_agent.py` 能力边界：`docker_runtime_adapter=True`，但 `sandbox=False`。
- 新增 ADR-0023，并同步活跃任务、Sprint、学习笔记、资料库、架构状态和下一步门禁。
- 生成 Week 5 Day 5 面试题，等待用户回答后才能归档并进入 Day 6。

## 验证

- `E:\python\Scripts\pytest.exe tests\test_docker_runtime.py -q`：先 RED，最终 `4 passed`。
- `E:\python\Scripts\pytest.exe tests\test_examples.py::test_permission_agent_example_reports_allow_deny_and_ask_paths -q`：先 RED，最终 `1 passed`。
- `E:\python\Scripts\pytest.exe tests\test_docker_runtime.py tests\test_runtime_interface.py tests\test_shell_runtime.py -q`：`32 passed`。
- `E:\python\Scripts\pytest.exe tests\test_workspace.py tests\test_checkpoints.py tests\test_git_checkpoints.py tests\test_docker_runtime.py tests\test_runtime_interface.py -q`：`25 passed`。
- `E:\python\Scripts\pytest.exe tests\test_examples.py -q`：`4 passed`。
- `E:\python\Scripts\pytest.exe -q`：`163 passed, 1 skipped`。
- 四个示例脚本均通过。
- `python -m compileall src examples -q`：沙箱内因 `__pycache__` 写权限失败；提升权限复跑通过。
