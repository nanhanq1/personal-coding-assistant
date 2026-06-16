# Weekly Sprints

本文件保留活跃 Sprint 入口。完整 24 周计划见 `docs/14_24_WEEK_PLAN.md`。

## Sprint 共同原则

- 每周交付一个可运行、可测试、可验收的能力切片。
- 每周至少覆盖一个失败路径或安全边界。
- 每周更新测试、文档、实现日志、下一步行动和面试题状态。
- 每 2 周实现后安排 1 周工业级加固；加固周不新增大模块。
- 文档不能宣称源码没有实现的能力。

## 当前 Sprint：Week 3 - Agent Core + Tool Runtime 工业级加固

### 1. 本周主题

修正当前状态漂移，并把 Week 1-2 的 Agent Core + Tool Runtime 主链加固到具备初步 trace、统计、输出截断和资源边界。

### 2. 本周工业级目标

- 文档与源码状态一致。
- `ToolResult` 支持必要元数据。
- `ToolRegistry` 能记录调用统计。
- shell/file 输出支持截断。
- 文件工具具备文件大小和二进制检测边界。

### 3. 核心概念

- trace_id
- tool_call_id
- structured log
- output truncation
- resource limit
- registry stats

### 4. 参考项目

- mini-SWE-agent：线性 trajectory 和最小 runtime。
- OpenHands：event stream 和 runtime 轨迹。
- LangChain：tracing / callback 抽象。

### 5. 代码模块

- `src/pca/core/events.py`
- `src/pca/observability/logger.py`
- `src/pca/tools/base.py`
- `src/pca/tools/registry.py`
- `src/pca/tools/file_tools.py`
- `src/pca/runtime/shell_runtime.py`

### 6. 测试任务

- trace id 生成和透传测试。
- `ToolResult` 兼容性测试。
- `ToolRegistry` 统计测试。
- shell 输出截断测试。
- 文件大小限制和二进制检测测试。

### 7. 文档任务

- 更新 `README.md` 当前真实状态。
- 更新 `docs/09_NEXT_ACTIONS.md`。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`。
- 新增或更新 ADR。
- 更新 Week 3 学习笔记。

### 8. 验收标准

```powershell
python -m pytest -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python -m compileall src examples -q
```

新增示例：

```powershell
python examples\03_observed_tool_run.py
```

### 9. 常见风险

- 把 observability 写成散落的 `print`。
- 新字段破坏旧测试兼容。
- 截断后 LLM 不知道内容被截断。
- 文件大小限制误伤正常小文件。

### 10. 本周完成后新增能力

一次工具调用可以带 trace、统计和截断信息；文件与命令输出具备基本资源边界。

## 当前周每日安排

| Day | 学习目标 | 代码任务 | 测试任务 | 文档任务 | 完成标准 |
|---|---|---|---|---|---|
| 1 | 修正文档状态漂移 | 不改源码 | 跑当前基线 | README/Next Actions/日志 | 文档与源码一致 |
| 2 | trace 数据结构 | `TraceContext`、`AgentEvent` | trace 单测 | ADR 草稿 | 单测通过 |
| 3 | ToolResult 元数据 | `trace_id/tool_call_id/output_truncated` | 兼容测试 | 架构更新 | 旧/新测试通过 |
| 4 | Registry 统计 | `get_stats()` | stats 测试 | 学习笔记 | stats 可查询 |
| 5 | 输出截断 | shell/file result 截断 | 大输出测试 | 安全边界 | 截断可见 |
| 6 | 文件资源限制 | size/binary 检测 | 文件边界测试 | ADR 完成 | 文件边界通过 |
| 7 | 加固验收 | 示例脚本 | 全量+示例+编译 | 面试题 | 可进入 Week 4 |
