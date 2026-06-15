# Learning Notes

本文件只保留**当前模块**的学习笔记。历史记录已归档到 `docs/archive/learning_notes/`。

## 当前模块：工业级加固（第 1-2 周加固周）

### 核心概念

| 概念 | 一句话解释 | 代码位置 |
|---|---|---|
| 结构化日志 | 用 JSON 格式记录操作，不是 print | `src/pca/core/observability.py` |
| trace_id | 贯穿整个调用链的唯一标识 | `src/pca/core/observability.py` |
| 输出截断 | 防止大量输出撑爆 message history | `src/pca/tools/base.py` → `truncate_output()` |
| 调用统计 | 记录每个工具的调用次数、成功率、耗时 | `src/pca/tools/registry.py` → `get_stats()` |
| AgentLoopStats | 一次 Agent 运行的资源消耗统计 | `src/pca/core/agent_loop.py` |

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

### 加固执行流程

现状评估 → 优先级排序 → 逐项加固 → 集成验证 → 真实验证 → 文档更新 → 验收签字

## 历史笔记索引

| 周次 | 主题 | 归档文件 |
|---|---|---|
| 第 1 周 | Agent Loop | `docs/archive/learning_notes/week1-2.md` |
| 第 2 周 | Tool System | `docs/archive/learning_notes/week1-2.md` |
