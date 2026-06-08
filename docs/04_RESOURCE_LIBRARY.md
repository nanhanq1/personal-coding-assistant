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

### Tool Registry / Tool Calling from Scratch

- 学习目的：理解为什么真实 Agent 需要工具注册表，而不是把工具散落在普通字典或 if/else 中。
- 建议阅读：优先看工具 name、description、arguments、result 这几个字段如何贯穿一次调用。
- 和本项目的关系：Day 2 的 `Tool` / `ToolRegistry` 是后续文件工具、shell runtime、权限系统和 MCP tool bridge 的基础。

### Day 3 文件工具资料

- Python `pathlib` 官方文档：https://docs.python.org/3/library/pathlib.html
- pytest `tmp_path` 官方文档：https://docs.pytest.org/en/stable/how-to/tmp_path.html
- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- Microsoft Learn Python on Windows 路径说明：https://learn.microsoft.com/en-us/windows/python/
- Real Python `pathlib` 视频课程：https://realpython.com/videos/pathlib-python-overview/

### Day 4 shell runtime 资料

- Python `subprocess` 官方文档：https://docs.python.org/3/library/subprocess.html
- pytest monkeypatch 官方文档：https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- PowerShell `pwsh` 命令行说明：https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pwsh
- Python `locale` 官方文档：https://docs.python.org/3/library/locale.html

### Day 5 Loop + Tools 整合资料

- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling
- Claude tool use overview：https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- mini-SWE-agent GitHub：https://github.com/SWE-agent/mini-swe-agent
- mini-SWE-agent CLI docs：https://mini-swe-agent.com/latest/usage/mini/

### Day 6 文档和架构图资料

- ReAct 论文 arXiv 页面：https://arxiv.org/abs/2210.03629
- Google Research ReAct 介绍：https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/
- Mermaid 官方语法参考：https://mermaid.js.org/intro/syntax-reference.html
- GitHub Docs：README 和个人资料 README 说明：https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling

### Day 7 周复盘和小重构资料

- pytest assertion 官方文档：https://docs.pytest.org/en/stable/how-to/assert.html
- Python `pathlib` 官方文档：https://docs.python.org/3.11/library/pathlib.html
- Mermaid 官方语法参考：https://mermaid.js.org/intro/syntax-reference.html
- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling

## 视频搜索关键词

| 关键词 | 学习目的 |
| --- | --- |
| `AI Agents from scratch tool calling tutorial` | 理解最小 Agent Loop 和工具调用 |
| `AI agent tool registry Python` | 理解工具注册表的最小实现方式 |
| `Claude Code architecture agent harness` | 理解 Claude Code-like harness |
| `OpenAI Agents SDK tutorial tools handoffs tracing` | 学习标准 Agent SDK |
| `mini SWE agent architecture bash trajectory` | 学习 shell runtime 和 trajectory |
| `Python pathlib tutorial` | 学习路径解析和文件读写 |
| `pytest tmp_path tutorial` | 学习隔离文件系统测试 |
| `Python subprocess timeout cwd stdout stderr tutorial` | 学习命令执行输入输出和超时 |
| `shell command sandbox workspace root safety` | 学习 shell runtime 安全边界 |

## 长期资料池

- learn-claude-code：Agent Harness、tools、permission、MCP、context、memory。
- MCP Specification：Host、Client、Server、Tools、Resources、Prompts、JSON-RPC。
- LangGraph Docs：StateGraph、checkpoint、human-in-the-loop、durable execution。
- Aider Docs：repo map、代码库上下文、diff、git commit、测试反馈。
- Cline Docs：Plan/Act、MCP、approval、checkpoints、IDE Agent。
- OpenHands Docs / GitHub：runtime、sandbox、workspace、Software Agent SDK。
- Mem0 / Letta / Graphiti / Zep：长期记忆和 temporal knowledge graph。
- LlamaIndex Docs：RAG、Workflows、Agentic Document Workflows。
