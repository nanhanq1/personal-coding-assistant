# Resource Library

## 今日优先资料

### ReAct: Synergizing Reasoning and Acting in Language Models

- 论文解决的问题：LLM 只推理不行动，无法通过外部环境获得新信息。
- 核心思想：把 reasoning trace 和 action 交替组织，让模型边想边调用工具。
- 和本项目的关系：Agent Loop 的理论基础就是 `think -> act -> observe -> continue`。
- 应该读哪几节：Abstract、Introduction、Method。

### mini-SWE-agent

- 学习目的：理解最小 Coding Agent 如何通过 bash / shell 完成真实代码任务。
- 建议阅读：先找 agent loop、environment、trajectory 相关代码。

### OpenAI Agents SDK

- 学习目的：理解 Agent、Runner、Tools、Tracing 等标准抽象。
- 建议阅读：先看 Tools 和 Runner 的基本示例。

## 视频搜索关键词

| 关键词 | 学习目的 |
| --- | --- |
| `AI Agents from scratch tool calling tutorial` | 理解最小 Agent Loop 和工具调用 |
| `Claude Code architecture agent harness` | 理解 Claude Code-like harness |
| `OpenAI Agents SDK tutorial tools handoffs tracing` | 学习标准 Agent SDK |
| `mini SWE agent architecture bash trajectory` | 学习 shell runtime 和 trajectory |

## 长期资料池

- learn-claude-code：Agent Harness、tools、permission、MCP、context、memory。
- MCP Specification：Host、Client、Server、Tools、Resources、Prompts、JSON-RPC。
- LangGraph Docs：StateGraph、checkpoint、human-in-the-loop、durable execution。
- Aider Docs：repo map、代码库上下文、diff、git commit、测试反馈。
- Cline Docs：Plan/Act、MCP、approval、checkpoints、IDE Agent。
- OpenHands Docs / GitHub：runtime、sandbox、workspace、Software Agent SDK。
- Mem0 / Letta / Graphiti / Zep：长期记忆和 temporal knowledge graph。
- LlamaIndex Docs：RAG、Workflows、Agentic Document Workflows。

