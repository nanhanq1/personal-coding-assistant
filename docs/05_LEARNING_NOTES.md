# Learning Notes

本文件只保留**当前模块**的学习笔记。历史记录已归档到 `docs/archive/learning_notes/`。

## 当前模块：Week 3 Agent Core + Tool Runtime 工业级加固

### 核心概念

| 概念 | 一句话解释 | 当前状态或目标位置 |
|---|---|---|
| 结构化日志 | 用结构化事件记录操作，不是散落的 `print` | 目标位置：`src/pca/observability/logger.py`，当前仍是占位 |
| trace_id | 贯穿一次 Agent 运行或工具调用链的唯一标识 | 已有最小结构：`src/pca/core/events.py` 的 `TraceContext` |
| AgentEvent | 描述 Agent loop、工具调用、工具结果等运行事件 | 已有最小结构：`src/pca/core/events.py` 的 `AgentEvent`，尚未接入主链 |
| 输出截断 | 防止大量 stdout、stderr 或文件内容撑爆 message history | 目标位置：`src/pca/tools/base.py` 或具体 tool/runtime 边界 |
| 调用统计 | 记录每个工具的调用次数、成功率、耗时 | 目标位置：`src/pca/tools/registry.py` → `get_stats()` |
| 文件资源边界 | 限制文件大小并识别二进制文件，避免误读不可处理内容 | 目标位置：`src/pca/tools/file_tools.py` |

### 九个工业级维度（精简版）

详细标准见 `docs/INDUSTRIAL_STANDARDS.md`。

1. **可观测性**：trace_id + 结构化日志 + 调用统计
2. **健壮性**：输入校验 + 错误分级 + 重试 + 超时
3. **安全性**：权限控制 + 审计日志 + 脱敏 + 资源限制
4. **性能**：基准测试 + 截断机制 + 资源上限
5. **可测试性**：覆盖率 ≥ 90% + 集成测试 + 回归测试
6. **接口清晰性**：完整文档 + 稳定接口 + 有意义错误信息
7. **可扩展性**：职责单一 + 依赖注入 + 预留扩展点
8. **代码质量**：中文注释 + 有意义命名 + 短小函数 + DRY
9. **真实验证**：用真实代码库验证，不只是单元测试

### 当前边界

- 已实现主链仍是 `AgentLoop`、`ToolRegistry`、`ToolResult`、文件工具和 `ShellRuntime`。
- `src/pca/observability/` 当前是占位目录，不能宣传为已接入主链。
- Week 3 Day 2 已实现轻量 trace 数据结构，但尚未接入 `AgentLoop`、`ToolResult` 或 `ToolRegistry`。

### 加固执行流程

现状评估 -> 状态纠偏 -> trace 数据结构 -> ToolResult 元数据 -> Registry stats -> 输出截断 -> 文件资源边界 -> 集成验证 -> 真实验证 -> 文档更新 -> 验收签字

## 历史笔记索引

| 周次 | 主题 | 归档文件 |
|---|---|---|
| 第 1 周 | Agent Loop | `docs/archive/learning_notes/week1-2.md` |
| 第 2 周 | Tool System | `docs/archive/learning_notes/week1-2.md` |
