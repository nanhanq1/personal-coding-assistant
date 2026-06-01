# Architecture Decisions

## ADR-0002：第 1 周 Day 2 使用 ToolRegistry 管理工具调用

日期：2026-06-01

### 背景

Day 1 的 `AgentLoop` 直接接收 `dict[str, callable]`。这种方式能完成最小闭环，但随着工具数量增加，会缺少统一的工具元数据、注册入口、错误处理和执行边界。

### 决策

新增 `Tool` 和 `ToolRegistry`：

- `Tool` 负责包装单个工具的名称、描述和 handler。
- `ToolRegistry` 负责注册、查找和执行工具。
- `AgentLoop` 只调用 `ToolRegistry.run(tool_call.name, tool_call.arguments)`，不直接依赖具体工具函数。

### 理由

- 让 Agent Loop 保持简单，只关注 LLM 消息和工具调用流程。
- 为后续文件工具、shell 工具、权限系统和工具 schema 留出扩展点。
- 让未知工具、重复注册等错误集中在工具系统内部处理。
- 更接近真实 Coding Agent 的工具路由结构。

### 暂不采用

- 暂不实现 JSON Schema 参数校验。
- 暂不实现异步工具。
- 暂不实现权限审批和危险工具拦截，这些留到后续模块。

## ADR-0001：第 1 天使用 mock LLM 而不接入真实 API

日期：2026-05-26

### 背景

当前目标是理解并实现最小 Agent Loop，而不是测试模型能力或 API 接入。

### 决策

使用可脚本化的 mock LLM 来稳定地产生 tool call 和最终回答。

### 理由

- 初学阶段更容易观察 Agent Loop 的控制流。
- 测试可重复，不受网络、API key、模型输出随机性影响。
- 后续可以把 mock LLM 替换为真实 LLM adapter，而不改 Agent Loop 的主结构。

### 暂不采用

- 暂不接入真实 OpenAI / Anthropic API。
- 暂不实现复杂 tool schema。
- 暂不实现多轮规划、权限和 RAG。
