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

### Week 2 Day 1 工具 schema 资料

- JSON Schema object 参考：https://json-schema.org/understanding-json-schema/reference/object
- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling
- Python `dataclasses` 官方文档：https://docs.python.org/3/library/dataclasses.html
- 建议阅读顺序：先看 JSON Schema 的 `properties`、`required` 和 `additionalProperties`，再看 OpenAI tool calling 如何把函数名、描述和参数 schema 提供给模型，最后复习 `dataclass` 如何表达轻量数据结构。

### Week 2 Day 2 工具 schema 与 LLM adapter 资料

- OpenAI Function calling / tool calling guide：https://developers.openai.com/api/docs/guides/function-calling
- OpenAI Using tools guide：https://developers.openai.com/api/docs/guides/tools
- Anthropic Tool use overview：https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Anthropic Define tools：https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- JSON Schema object 参考：https://json-schema.org/understanding-json-schema/reference/object
- 建议阅读顺序：先看 OpenAI function calling 中工具 schema 与 strict mode 的要求，再看 Anthropic define tools 中 `name`、`description`、`input_schema` 和工具描述质量要求，最后回到本项目理解为什么当前先保持内部中立 schema。

### Week 2 Day 3 `edit_file` 局部编辑资料

- Python `difflib` 官方文档：https://docs.python.org/3/library/difflib.html
- GNU diffutils `patch` 手册：https://www.gnu.org/software/diffutils/manual/html_node/Merging-with-patch.html
- Real Python `pathlib` 教程：https://realpython.com/python-pathlib/
- 建议阅读顺序：先复习 `pathlib` 的路径读写和边界意识，再看 `difflib.unified_diff(...)` 如何表达文本差异，最后了解 `patch` 为什么需要上下文来把 diff 应用到文件。当前项目 Day 3 只实现精确文本替换，diff/patch 属于后续升级方向。

### Week 2 Day 4 结构化 tool result 资料

- Python `dataclasses` 官方文档：https://docs.python.org/3/library/dataclasses.html
- Python `time.perf_counter()` 官方文档：https://docs.python.org/3/library/time.html
- OpenTelemetry Observability Primer：https://opentelemetry.io/docs/concepts/observability-primer/
- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- 建议阅读顺序：先复习 `dataclass` 如何表达轻量结果对象，再看 `perf_counter()` 为什么适合测量工具执行耗时，然后用 OpenTelemetry 的 observability primer 理解成功、失败、耗时和错误字段为什么是后续 trace 的基础，最后回到 Agents SDK Tools 文档观察标准 Agent 工具如何被描述和调用。

### Week 2 Day 5 整合 schema + edit_file + result 资料

- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- mini-SWE-agent GitHub：https://github.com/SWE-agent/mini-swe-agent
- Anthropic Tool use overview：https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- LangChain Tools 文档：https://docs.langchain.com/oss/python/langchain/tools
- 建议阅读顺序：先看 OpenAI Agents SDK 如何把工具作为 Agent 可执行动作，再看 mini-SWE-agent 如何通过简单工具链完成软件工程任务，然后对比 Anthropic 和 LangChain 对工具描述、参数和执行结果的组织方式，最后回到本项目理解为什么 Day 5 只整合链路、不提前接真实 adapter。

### Week 2 Day 6 文档和面试表达资料

- Mermaid 官方语法参考：https://mermaid.js.org/intro/syntax-reference.html
- GitHub Docs：README 说明：https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- Anthropic Tool use overview：https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- mini-SWE-agent GitHub：https://github.com/SWE-agent/mini-swe-agent
- 建议阅读顺序：先用 Mermaid 把第 2 周工具链路画清楚，再用 GitHub README 指南检查外部读者能否快速理解项目，最后对照 OpenAI / Anthropic / mini-SWE-agent 的工具表达方式，打磨自己的面试讲解。

### Week 2 Day 7 周复盘和 env 输出脱敏资料

- Python `subprocess` 官方文档：https://docs.python.org/3/library/subprocess.html
- Python `os.environ` 官方文档：https://docs.python.org/3/library/os.html#os.environ
- OWASP 环境变量信息暴露说明：https://owasp.org/www-community/vulnerabilities/Information_exposure_through_environment_variables
- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- 建议阅读顺序：先看 `subprocess.run(..., env=...)` 如何把环境变量传给子进程，再看 `os.environ` 理解环境变量的进程边界，最后用 OWASP 信息暴露说明理解为什么工具输出不能把 secret 原样写回 Agent 轨迹。

### Week 3 Day 4 ToolRegistry 调用统计资料

- pytest assertion 官方文档：https://docs.pytest.org/en/stable/how-to/assert.html
- Python `time.perf_counter()` 官方文档：https://docs.python.org/3/library/time.html
- OpenTelemetry Traces 概念文档：https://opentelemetry.io/docs/concepts/signals/traces/
- mini-SWE-agent GitHub：https://github.com/SWE-agent/mini-swe-agent
- 建议阅读顺序：先用 pytest assertion 理解如何写 stats 行为测试，再复习 `perf_counter()` 为什么适合测量工具耗时，然后看 OpenTelemetry trace 文档区分“单次链路”和“聚合统计”，最后对照 mini-SWE-agent 的运行轨迹理解为什么工具调用历史需要可观察。

### Week 3 Day 5 输出截断资料

- Python `subprocess.run` 输出捕获文档：https://docs.python.org/3/library/subprocess.html#subprocess.run
- pytest `tmp_path` 官方文档：https://docs.pytest.org/en/stable/how-to/tmp_path.html
- OpenHands GitHub：https://github.com/OpenHands/OpenHands
- OpenHands Docs：https://docs.openhands.dev/overview/introduction
- 建议阅读顺序：先复习 `subprocess.run(..., capture_output=True, text=True)` 如何产生 stdout/stderr，再用 pytest `tmp_path` 构造隔离的大文件输出测试，然后对照 OpenHands 的 agent/runtime 项目结构理解为什么工具 observation 不能无限写回轨迹。

### Week 3 Day 6 文件资源限制资料

- Python `Path.stat()` 官方文档：https://docs.python.org/3/library/pathlib.html#pathlib.Path.stat
- Python 文件读写模式官方教程：https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
- pytest `tmp_path` 官方文档：https://docs.pytest.org/en/stable/how-to/tmp_path.html
- OpenHands GitHub：https://github.com/OpenHands/OpenHands
- OpenHands Docs：https://docs.openhands.dev/overview/introduction
- 建议阅读顺序：先看 `Path.stat().st_size` 如何在读取前获得文件大小，再看二进制模式 `open("rb")` 如何采样字节，最后对照 OpenHands 的 runtime/workspace 设计理解为什么真实 Agent 需要在工具边界设置资源限制。

### Week 4 Day 1 风险分类资料

- Cline Auto Approve & YOLO Mode：https://docs.cline.bot/features/auto-approve
- OWASP Command Injection：https://owasp.org/www-community/attacks/Command_Injection
- MCP Security Best Practices：https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- MIT 6.858 Computer Systems Security：https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/
- OpenHands GitHub：https://github.com/OpenHands/OpenHands
- 建议阅读顺序：先看 Cline 如何区分 safe command 和 approval-required command，再看 OWASP 命令注入理解 shell 字符串风险，然后用 MCP security 文档理解 consent、scope 和 audit 为什么属于权限系统边界。

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
| `Python difflib unified diff tutorial` | 学习如何表达局部文本差异 |
| `apply patch algorithm context lines` | 理解 patch 工具为什么需要上下文 |
| `Python subprocess timeout cwd stdout stderr tutorial` | 学习命令执行输入输出和超时 |
| `shell command sandbox workspace root safety` | 学习 shell runtime 安全边界 |
| `python metrics counters success failure duration tutorial` | 学习调用统计的最小指标设计 |
| `agent tool output truncation stdout stderr observation` | 学习工具输出截断和 observation 预算 |
| `coding agent file size limit binary detection` | 学习文件工具读取前资源限制 |
| `coding agent command approval permission risk classification` | 学习命令风险分类和审批边界 |

## 长期资料池

- learn-claude-code：Agent Harness、tools、permission、MCP、context、memory。
- MCP Specification：Host、Client、Server、Tools、Resources、Prompts、JSON-RPC。
- LangGraph Docs：StateGraph、checkpoint、human-in-the-loop、durable execution。
- Aider Docs：repo map、代码库上下文、diff、git commit、测试反馈。
- Cline Docs：Plan/Act、MCP、approval、checkpoints、IDE Agent。
- OpenHands Docs / GitHub：runtime、sandbox、workspace、Software Agent SDK。
- Mem0 / Letta / Graphiti / Zep：长期记忆和 temporal knowledge graph。
- LlamaIndex Docs：RAG、Workflows、Agentic Document Workflows。
