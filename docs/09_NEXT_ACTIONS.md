# Next Actions

## 必读文件

每次会话开始前：`AGENTS.md`、`docs/INDEX.md`

继续项目时追加：`docs/00_PROJECT_CONTEXT.md`、`docs/01_LEARNING_ROADMAP.md`、`docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`

## 当前状态

- **路线阶段**：12 周路线，第 2 周已完成，进入工业级加固
- **当前主题**：第 1-2 周 Agent Loop + Tool System 工业级加固
- **最新测试**：`pytest -q` 为 `93 passed, 1 skipped`
- **最新示例**：`python examples/01_minimal_agent.py` 正常输出
- **阻塞项**：无

## 已完成的工业级加固

- 新增 `src/pca/core/observability.py`：结构化日志、trace_id、调用统计、审计日志
- 更新 `src/pca/core/messages.py`：Message 和 ToolCall 添加 id + timestamp
- 更新 `src/pca/tools/base.py`：ToolResult 添加 trace_id、tool_call_id、output_truncated；新增 truncate_output()
- 更新 `src/pca/core/agent_loop.py`：添加 AgentLoopStats、trace_id 透传、结构化日志

## 待完成的加固工作

1. 更新 `src/pca/tools/registry.py`：添加调用统计、日志、trace 透传
2. 更新 `src/pca/tools/file_tools.py`：添加文件大小限制、二进制检测
3. 更新 `src/pca/runtime/shell_runtime.py`：添加命令审计、输出截断
4. 补充测试确保兼容性
5. 运行完整测试套件验证

## 下一步行动

继续第 1-2 周工业级加固：按 Phase 3-4 顺序完成 ToolRegistry、File Tools、Shell Runtime 的加固，然后补充测试和文档。

## 用户下次应发送的指令

```text
继续项目，继续工业级加固。
```
