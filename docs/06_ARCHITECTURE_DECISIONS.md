# Architecture Decisions

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

