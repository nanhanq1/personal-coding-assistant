# Reference Project Mapping

本文件把外部工业级项目映射到本项目路线。读取外部项目时只学习机制，不照搬整体架构。

> 说明：本映射在 2026-06-15 复核了公开 GitHub 入口；具体目录可能随上游变化，开始对应周任务前需要再打开上游仓库确认。

## 总表

| 项目 | 本项目对应模块 | 重点学习 | 不照搬 |
|---|---|---|---|
| mini-SWE-agent | Agent Core、Runtime、E2E coding loop | 极简 loop、线性 trajectory、bash-only baseline、subprocess/sandbox 替换思想 | 不把 shell 当唯一工具；本项目保留结构化工具系统 |
| Aider | Repo map、diff、git workflow | repo map、文件选择、patch/diff、commit 工作流 | 不照搬完整聊天 UI 和模型适配复杂度 |
| Cline | IDE Agent、approval、工具交互 | Plan/Act、权限审批、用户交互、MCP 工具体验 | 不绑定 VS Code extension 作为核心 |
| OpenHands | Workspace、sandbox、event、runtime | sandbox、event stream、workspace、agent platform 边界 | 不做多 agent 平台和浏览器环境大而全 |
| Khoj | Personal Assistant、knowledge base、automation | 个人知识库、文档搜索、自定义 agent、任务自动化 | 不做完整多端产品和云服务 |
| Letta | Long-term memory、stateful agents | 记忆块、状态化 agent、记忆生命周期 | 不复制 server platform 和多用户 API |
| Mem0 | Memory layer | 记忆抽取、写入策略、检索 API、用户级 memory | 不引入外部服务作为核心依赖 |
| Graphiti | Temporal knowledge graph | 事件记忆、实体关系、时间有效性 | 不一开始做复杂图数据库 |
| Zep | Context engineering、graph memory | 关系感知 context assembly、Graph RAG、低延迟上下文块 | 不依赖 Zep Cloud 或企业服务 |
| LangGraph | State machine、durable workflow | StateGraph、节点、边、checkpoint、human-in-the-loop | 不把框架作为早期必需依赖 |
| LangChain | Common abstractions | Messages、Tools、Retrievers、Document Loaders、Text Splitters、Vector Stores、Tracing | 不把项目变成 LangChain wrapper |

## mini-SWE-agent

- 来源：`https://github.com/SWE-agent/mini-swe-agent`
- 上游信号：README 强调极简 agent、线性 history、只用 bash、`subprocess.run` 和 sandbox 可替换。
- 读什么：`src/minisweagent`、agent class、environment、model、run script、tests。
- 学什么：
  - 最小 Coding Agent loop 如何保持线性轨迹。
  - 为什么独立 `subprocess.run` action 容易切到 Docker/sandbox。
  - 如何用 benchmark/E2E 验证 agent，而不是只看单元测试。
- 对应本项目：
  - `src/pca/core/agent_loop.py`
  - `src/pca/runtime/shell_runtime.py`
  - 后续 `tests/e2e/`
- 仿写能力：
  - 线性 trajectory 的可回放表达。
  - runtime adapter 可替换接口。
- 不照搬：
  - bash-only。PCA 需要文件工具、git 工具、memory 工具和权限元数据。

## Aider

- 来源：`https://github.com/Aider-AI/aider`
- 读什么：repo map、coder、diff/edit、git 相关目录和测试。
- 学什么：
  - repo map 如何帮助模型选择文件。
  - 修改代码如何形成可审查 diff。
  - commit message 和 git workflow 如何融入 coding loop。
- 对应本项目：
  - `src/pca/coding/repo_scanner.py`
  - `src/pca/coding/repo_map.py`
  - `src/pca/coding/patcher.py`
  - `src/pca/tools/git_tools.py`
- 仿写能力：
  - repo map 数据结构。
  - diff review 和 commit 候选生成。
- 不照搬：
  - 不复制 Aider 的完整 terminal chat 产品。
  - 不把所有逻辑塞进单个 coder 对象。

## Cline

- 来源：`https://github.com/cline/cline`
- 读什么：工具定义、approval/human interaction、MCP 集成、任务状态流。
- 学什么：
  - IDE Agent 为什么需要审批和用户确认。
  - Plan/Act 模式如何影响交互体验。
  - 工具执行前如何展示风险和参数。
- 对应本项目：
  - `src/pca/permissions/risk.py`
  - `src/pca/permissions/policy.py`
  - `src/pca/permissions/approval.py`
  - `src/pca/cli.py`
- 仿写能力：
  - 审批请求对象和用户决策记录。
  - 高风险工具调用前的解释文本。
- 不照搬：
  - 不把 VS Code extension 作为核心运行环境。

## OpenHands

- 来源：`https://github.com/OpenHands/OpenHands`
- 读什么：runtime、sandbox、events、workspace、evaluation 相关目录。
- 学什么：
  - Workspace 和 sandbox 的边界。
  - Agent action / observation / event stream 的结构。
  - 软件工程任务评估和轨迹记录。
- 对应本项目：
  - `src/pca/runtime/workspace.py`
  - `src/pca/runtime/docker_runtime.py`
  - `src/pca/core/events.py`
  - `src/pca/observability/replay.py`
- 仿写能力：
  - event stream。
  - workspace abstraction。
  - sandbox runtime 接口。
- 不照搬：
  - 不做完整 OpenHands 平台，不引入浏览器和多 agent 大框架作为早期核心。

## Khoj

- 来源：`https://github.com/khoj-ai/khoj`
- 上游信号：README 定位为 AI second brain，支持本地/在线模型、文档问答、自定义 agents、自动化和语义搜索。
- 读什么：`src`、documentation、搜索/索引/agent/automation 相关代码。
- 学什么：
  - 个人知识库如何组织文档、搜索和 agent persona。
  - 自动化任务如何与个人上下文结合。
  - 自托管产品如何组织文档和配置。
- 对应本项目：
  - `src/pca/memory`
  - `src/pca/retrieval`
  - `src/pca/context`
  - `src/pca/cli.py`
- 仿写能力：
  - 知识库 loader + search + answer flow。
  - custom agent profile。
- 不照搬：
  - 不做完整 Web/移动/WhatsApp/云端多端产品。

## Letta / Mem0

- 来源：
  - `https://github.com/letta-ai/letta`
  - `https://github.com/mem0ai/mem0`
- 读什么：memory abstractions、agent state、memory update/retrieval、tests、examples。
- 学什么：
  - 长期记忆如何写入、检索、更新和删除。
  - 如何区分用户偏好、任务事实、项目状态和普通对话摘要。
  - memory 作为 agent state，而不是普通向量库。
- 对应本项目：
  - `src/pca/memory/base.py`
  - `src/pca/memory/preference_memory.py`
  - `src/pca/memory/project_memory.py`
  - `src/pca/memory/task_memory.py`
- 仿写能力：
  - memory write candidate。
  - memory lifecycle policy。
  - memory retrieval evaluation。
- 不照搬：
  - 不做服务端平台和多租户 memory API。

## Graphiti / Zep

- 来源：
  - `https://github.com/getzep/graphiti`
  - `https://github.com/getzep/zep`
- 上游信号：Zep README 强调 temporal knowledge graph、relationship-aware context、context assembly。
- 读什么：Graphiti 的实体/关系/episode/temporal 代码，Zep 的 examples、integrations、eval harness。
- 学什么：
  - 个人状态图谱如何表达“事实随时间变化”。
  - 事件记忆如何转成实体关系。
  - Graph RAG 如何组装上下文。
- 对应本项目：
  - `src/pca/memory/graph_memory.py`
  - `src/pca/graph/state_graph.py`
  - `src/pca/context/personal_context.py`
- 仿写能力：
  - entity/relation/event 数据模型。
  - `valid_from/valid_to` 或等价时间字段。
- 不照搬：
  - 不引入完整图数据库作为早期依赖；先用 SQLite/JSONL 建模。

## LangGraph

- 来源：`https://github.com/langchain-ai/langgraph`
- 读什么：state graph、checkpoint、interrupt、human-in-the-loop 示例。
- 学什么：
  - 节点和边如何表达复杂 agent workflow。
  - checkpoint 如何支持恢复。
  - human interrupt 如何插入审批。
- 对应本项目：
  - `src/pca/core/state_machine.py`
  - `src/pca/core/events.py`
  - `src/pca/runtime/checkpoints.py`
- 仿写能力：
  - 简化版 state machine。
  - planner/executor/reviewer 节点。
- 不照搬：
  - 不在早期把核心 AgentLoop 改成框架依赖。

## LangChain

- 来源：`https://github.com/langchain-ai/langchain`
- 读什么：messages、tools、retrievers、document loaders、text splitters、vector stores、tracing。
- 学什么：
  - 通用接口命名和抽象边界。
  - Document、Retriever、Tool、Message 的工程表达。
  - tracing 和 callback 的接口设计。
- 对应本项目：
  - `src/pca/core/messages.py`
  - `src/pca/tools/base.py`
  - `src/pca/retrieval`
  - `src/pca/observability`
- 仿写能力：
  - 中立接口，不绑定单个供应商。
  - loader/splitter/retriever/reranker 分层。
- 不照搬：
  - 不把 PCA 写成 LangChain wrapper；本项目目标是理解和实现核心机制。
