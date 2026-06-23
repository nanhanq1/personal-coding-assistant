# Architecture

## 当前真实架构

当前代码已经实现 `core + tools + runtime` 的最小可运行主链：

```mermaid
flowchart LR
    U["User input"] --> H["Message history"]
    H --> L["ScriptedLLM"]
    L --> A["assistant Message / ToolCall"]
    A --> Loop["AgentLoop"]
    Loop --> R["ToolRegistry.run"]
    R --> T["Tool.run"]
    T --> F["File tools"]
    T --> G["ShellCommandTool gate"]
    G --> P["classify_command + PermissionPolicy"]
    P -->|ALLOW| S["ShellRuntime"]
    P -->|ASK / DENY| TR
    F --> TR["ToolResult"]
    S --> TR
    TR --> M["AgentLoop._tool_result_to_message"]
    M --> H
```

真实已实现：

- `src/pca/core/messages.py`：`Message`、`ToolCall`
- `src/pca/core/mock_llm.py`：`ScriptedLLM`
- `src/pca/core/agent_loop.py`：`AgentLoop`、`AgentLoopResult`
- `src/pca/tools/base.py`：`Tool`、`ToolParameter`、`ToolResult`
- `src/pca/tools/registry.py`：`ToolRegistry`
- `src/pca/tools/file_tools.py`：`read_file`、`write_file`、`edit_file`
- `src/pca/runtime/shell_runtime.py`：`run_command`
- `src/pca/permissions/risk.py`：`RiskLevel`、`RiskAssessment`、`classify_command(...)`
- `src/pca/permissions/policy.py`：`DecisionAction`、`PermissionDecision`、`PermissionPolicy.decide(...)`
- `src/pca/permissions/approval.py`：`ApprovalRequest`、`ApprovalDecision`

当前部分实现但未接入主链：

- `src/pca/permissions`：风险分类和策略判断已接入 `ShellCommandTool` 执行前 gate；审批对象已实现但尚未接入交互式批准流程；audit 和文件风险 gate 仍未实现

当前仍是占位：

- `src/pca/context`
- `src/pca/memory`
- `src/pca/mcp`
- `src/pca/observability`
- `src/pca/runtime/checkpoints.py`
- `src/pca/runtime/docker_runtime.py`
- `src/pca/cli.py`

## 目标架构

```mermaid
flowchart TD
    CLI["CLI / optional UI"] --> Core["Agent Core"]
    Core --> Planner["Planner / State Machine"]
    Core --> Context["Context Builder"]
    Core --> Tools["Tool Runtime"]
    Core --> Memory["Memory Manager"]
    Core --> Obs["Observability"]

    Context --> Repo["Repo Map / Symbol Index"]
    Context --> RAG["Retrieval / RAG"]
    RAG --> Docs["Project Docs / Knowledge Base"]

    Tools --> Perm["Permission System"]
    Perm --> Runtime["Sandboxed Runtime"]
    Runtime --> Files["File Tools"]
    Runtime --> Shell["Command Runner"]
    Runtime --> Git["Git Tools"]
    Runtime --> Tests["Test/Lint/Type Runner"]

    Memory --> Pref["Preference Memory"]
    Memory --> Project["Project Memory"]
    Memory --> Learning["Learning Progress"]
    Memory --> Graph["Personal State Graph"]

    Obs --> Trace["Trace Store"]
    Obs --> Audit["Audit Log"]
    Obs --> Replay["Replay"]
    Obs --> Eval["Evaluation Reports"]
```

## 模块边界

| 模块 | 职责 | 禁止承担 |
|---|---|---|
| `core` | 消息结构、Agent loop、stop reason、tool result injection、event emission | 不直接读写文件、不直接执行 shell、不硬编码工具 |
| `tools` | 工具接口、schema、registry、结果信封、工具元数据、在具体工具边界调用权限策略 | 不内置风险规则，不做 sandbox |
| `runtime` | 工作区、命令执行、资源限制、checkpoint、rollback、sandbox adapter | 不决定业务权限，不构造 LLM prompt |
| `permissions` | 风险分类、策略判断、审批、审计事件 | 不执行命令，不修改文件 |
| `coding` | repo scan、symbol index、file relevance、patch/diff、test/lint/type/git workflow | 不保存长期个人记忆 |
| `context` | context budget、prompt builder、repo context assembly、compression | 不直接修改仓库 |
| `retrieval` | loader、chunking、BM25、vector、rerank、citation、retrieval eval | 不决定最终行动 |
| `memory` | preference、project、task、learning progress、write policy | 不直接进入 prompt，必须经 context builder |
| `graph` | personal state graph、entity/relation/event、temporal facts | 不替代普通 key-value memory |
| `observability` | structured logs、trace、audit、replay、stats | 不做业务决策 |
| `evaluation` | unit/integration/E2E/golden/regression/safety/RAG/memory eval harness | 不修改生产逻辑 |
| `cli` | 命令入口、交互、配置加载、用户审批输入 | 不承载核心业务逻辑 |

## 关键运行链路

### Coding Task

```mermaid
sequenceDiagram
    participant U as User
    participant C as CLI
    participant A as AgentCore
    participant X as ContextBuilder
    participant P as PermissionPolicy
    participant T as ToolRuntime
    participant O as Observability

    U->>C: request code change
    C->>A: start run
    A->>X: build repo context
    X-->>A: relevant files + citations
    A->>T: proposed tool call
    T->>P: classify and decide
    P-->>T: allow / ask / deny
    T-->>A: ToolResult
    A->>O: trace event
    A-->>U: final answer + diff + verification
```

### Memory Write

```mermaid
flowchart LR
    A["Agent event"] --> B["Memory candidate"]
    B --> C{"Write policy"}
    C -- "ignore" --> D["No write"]
    C -- "ask" --> E["User approval"]
    C -- "allow" --> F["Memory store"]
    E --> F
    F --> G["Trace + citation"]
```

## 依赖方向

高层模块可以依赖低层抽象，但不能反向依赖：

```text
cli -> core -> tools -> runtime
core -> context -> retrieval
core -> memory
tools -> permissions
all modules -> observability interfaces
evaluation -> all public interfaces
```

## 配置和安全边界

- 配置入口：后续新增 `src/pca/config.py`，从文件、环境变量和 CLI 参数加载。
- 密钥：只从环境变量读取；不写入 message history、logs、memory 或 docs。
- 工具执行：默认 workspace scoped；`run_command` 已经过最小 shell gate，`DENY` / `ASK` 不进入真实 shell runtime；破坏性文件操作、人工审批 UI、audit 和 sandbox 后续补齐。
- 输出：stdout/stderr、文件内容、检索结果和 memory recall 都必须支持截断。
- Git：commit/push 默认需要用户确认；自动 commit 只能在显式配置下启用。

## 作品集架构表达

作品集不宣称“生产级 SaaS”。准确表述为：

> 一个本地优先、可审计、可测试的 Personal Coding Assistant Agent。它实现了 coding workflow、权限边界、上下文检索、长期记忆、评估和可观测性，并明确列出未覆盖的企业级能力。
