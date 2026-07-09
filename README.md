# Personal Coding Assistant

一个学习优先、工程实践驱动的工业级 **Personal Coding Assistant** 项目。

本项目目标不是写 demo，而是从零实现一个可作为作品集展示的本地优先 Agent：它能理解代码仓库、调用工具、修改代码、运行验证、控制权限、沉淀长期记忆，并用测试、评估和文档证明真实工程质量。

## 当前真实进度

当前状态、测试基线、阻塞项和下一步只维护在 `docs/09_NEXT_ACTIONS.md`。

已实现主线与工业级差距见 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`；当前架构与目标架构见 `ARCHITECTURE.md`。

截至 2026-07-09，项目处于 Week 6 Day 1：Tool Runtime 加固周现状评估已完成，等待用户回答面试题后归档。当前最新验证基线为 `E:\python\Scripts\pytest.exe -q` 通过 `168 passed, 1 skipped`，5 个示例脚本通过，`python -m compileall src examples -q` 无错误输出。

## 核心架构

当前真实主链：

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
    F --> Q["file risk gate"]
    Q --> TR["ToolResult"]
    S --> TR
    TR --> M["AgentLoop._tool_result_to_message"]
    M --> H
    W["Workspace(root) independent boundary"]
    W --> Ck["FileCheckpoint API"]
    W --> Gk["GitCheckpoint API"]
    CR["CommandRuntime Protocol"] -.-> S
    CR -.-> Dk["DockerRuntime adapter"]
```

## 当前模块流程图

### 1. Core：消息与 AgentLoop

```mermaid
flowchart TD
    U["user_input"] --> A["AgentLoop.run"]
    A --> V{"非空字符串?"}
    V -- "否" --> E["ValueError"]
    V -- "是" --> H["message history<br/>追加 user Message"]
    H --> L["ScriptedLLM.complete(messages)"]
    L --> M{"返回 Message?"}
    M -- "否" --> T["TypeError"]
    M -- "是" --> AM["追加 assistant Message"]
    AM --> C{"包含 tool_calls?"}
    C -- "否" --> R["AgentLoopResult"]
    C -- "是" --> TC["逐个 ToolCall<br/>ToolRegistry.run"]
    TC --> TM["ToolResult -> tool Message"]
    TM --> H
```

### 2. Tools：工具抽象、参数 schema、注册表

```mermaid
flowchart TD
    A["create_coding_tool_registry"] --> B["read_file"]
    A --> C["write_file"]
    A --> D["edit_file"]
    A --> E["run_command"]

    X["ToolRegistry.run(name, arguments)"] --> V{"arguments 是 dict?"}
    V -- "否" --> F["ToolResult.failure"]
    V -- "是" --> G["ToolRegistry.get(name)"]
    G --> H{"工具存在?"}
    H -- "否" --> F
    H -- "是" --> I["Tool.run(arguments)"]
    I --> J["ToolParameter.validate"]
    J --> K{"参数通过?"}
    K -- "否" --> F
    K -- "是" --> L["执行 handler"]
    L --> M{"成功?"}
    M -- "否" --> F
    M -- "是" --> N["截断 stdout/stderr 或字符串输出"]
    N --> O["记录调用统计"]
    O --> P["ToolResult.success"]
```

### 3. File Tools：读写编辑、文件风险、失败回滚

```mermaid
flowchart TD
    A["read_file / write_file / edit_file"] --> B["解析 workspace_root"]
    B --> C["解析 path"]
    C --> D{"path 在 workspace 内?"}
    D -- "否" --> E["失败 ToolResult"]
    D -- "是" --> KIND{"工具类型"}

    KIND -- "read_file" --> R1{"小文本文件?<br/>非目录 / <=1MiB / 非明显二进制"}
    R1 -- "否" --> E
    R1 -- "是" --> R2["读取 UTF-8 文本"]

    KIND -- "write_file" --> W1["校验 content"]
    W1 --> W2["classify_file_change"]
    W2 --> W3["PermissionPolicy.decide"]

    KIND -- "edit_file" --> ED1["校验 old_text/new_text"]
    ED1 --> ED2["classify_file_change"]
    ED2 --> W3

    W3 --> G{"ALLOW / ASK / DENY"}
    G -- "ASK / DENY" --> E
    G -- "ALLOW" --> CK["FileCheckpoint.create"]
    CK --> OP["写入或精确替换"]
    OP --> OK{"写盘成功?"}
    OK -- "是" --> DONE["返回 ok"]
    OK -- "否" --> RB["FileCheckpoint.restore"]
    RB --> E
```

### 4. Shell Runtime：命令权限 gate 与本地执行

```mermaid
flowchart TD
    A["run_command ToolCall"] --> B["ShellCommandTool._run"]
    B --> C["classify_command"]
    C --> D["PermissionPolicy.decide"]
    D --> E{"决策"}
    E -- "DENY" --> F["PermissionError<br/>不进入 runtime"]
    E -- "ASK" --> G["PermissionError<br/>等待未来审批能力"]
    E -- "ALLOW" --> H["CommandRuntime.run"]
    H --> I["ShellRuntime.run"]
    I --> J["normalize command"]
    J --> K["resolve workspace_root"]
    K --> L["normalize timeout"]
    L --> M["resolve cwd<br/>必须在 workspace 内"]
    M --> N["build env"]
    N --> O["subprocess.run"]
    O --> P["stdout / stderr / returncode / timed_out"]
    P --> Q["敏感 env 输出脱敏"]
```

### 5. Permission：风险分类、策略、审批对象、审计对象

```mermaid
flowchart TD
    A["命令或文件变更"] --> B{"来源"}
    B -- "shell command" --> C["classify_command"]
    B -- "file change" --> D["classify_file_change"]
    C --> R["RiskAssessment<br/>SAFE / ASK / DENY"]
    D --> R
    R --> P["PermissionPolicy.decide"]
    P --> A1{"DecisionAction"}
    A1 -- "ALLOW" --> EX["允许进入副作用路径"]
    A1 -- "ASK" --> WAIT["当前返回 PermissionError"]
    A1 -- "DENY" --> BLOCK["阻断执行"]
    AR["ApprovalRequest / ApprovalDecision"] -. "已实现对象，未接入交互审批" .-> WAIT
    AU["PermissionAuditEvent / append_audit_event"] -. "独立 JSONL API，未自动接入 gate" .-> P
```

### 6. Runtime：Workspace、Checkpoint、Docker adapter

```mermaid
flowchart TD
    A["Workspace(root)"] --> B{"root 存在且是目录?"}
    B -- "否" --> E["ValueError"]
    B -- "是" --> C["resolve_path(path)"]
    C --> D{"路径在 root 内?"}
    D -- "否" --> E
    D -- "是" --> P["workspace 内绝对路径"]

    P --> FC["FileCheckpoint.create(paths)"]
    FC --> F1["记录文件是否存在和 bytes"]
    F1 --> FR["restore"]
    FR --> F2{"快照时存在?"}
    F2 -- "是" --> F3["写回原 bytes"]
    F2 -- "否" --> F4["删除新建文件"]

    A --> GC["GitCheckpoint.create"]
    GC --> G1["git diff --binary -- ."]
    G1 --> GR["restore"]
    GR --> G2["git restore --worktree -- ."]
    G2 --> G3["git apply 保存的 diff"]

    DR["DockerRuntime.run"] --> D1{"Docker CLI 和 daemon 可用?"}
    D1 -- "否" --> D2["fallback=docker_unavailable<br/>sandboxed=False"]
    D1 -- "是" --> D3["docker run<br/>挂载 workspace"]
```

### 7. 尚未接入主链的模块

```mermaid
flowchart TD
    A["当前主链<br/>core + tools + runtime + permission gate"] --> B["context 占位"]
    A --> C["memory 占位"]
    A --> D["mcp 占位"]
    A --> E["observability 占位"]
    A --> F["cli 占位"]
    A --> G["TraceContext / AgentEvent<br/>数据结构已实现，未自动透传"]
```

## 项目结构

```text
.
├── AGENTS.md                     # AI 执行规则
├── DOC_RULES.md                  # 文档写入和反漂移规则
├── PROJECT_REQUIREMENTS.md       # 最终项目需求和验收定义
├── ARCHITECTURE.md               # 当前架构和目标架构
├── EVALUATION.md                 # 测试、评估和 CI 策略
├── docs/
│   ├── INDEX.md                  # 文档索引
│   ├── 01_LEARNING_ROADMAP.md    # 24 周路线总览
│   ├── 02_DAILY_TASKS.md         # 当前活跃每日任务
│   ├── 03_WEEKLY_SPRINTS.md      # 当前活跃 Sprint
│   ├── 06_ARCHITECTURE_DECISIONS.md
│   ├── 07_IMPLEMENTATION_LOG.md
│   ├── 09_NEXT_ACTIONS.md
│   ├── 13_REFERENCE_PROJECT_MAPPING.md
│   ├── 14_24_WEEK_PLAN.md
│   ├── 15_MEMORY_SYSTEM.md
│   ├── 16_TEACHING_WORKFLOW.md
│   └── 17_WEEK6_HARDENING_REPORT.md
├── examples/
├── src/pca/
├── tests/
└── pyproject.toml
```

## 运行测试

```powershell
python -m pytest -q
```

## 运行示例

```powershell
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
```

## 24 周路线

完整计划见 `docs/14_24_WEEK_PLAN.md`。阶段如下：

| 阶段 | 周次 | 主题 |
|---|---:|---|
| A | 1-3 | Agent Core + Tool Runtime 基线与加固 |
| B | 4-6 | Permission + Sandbox + Git Safety |
| C | 7-10 | Coding Agent |
| D | 11-14 | Retrieval / RAG |
| E | 15-18 | Personal Assistant Memory |
| F | 19-20 | Planner / State Machine / Events |
| G | 21-22 | Evaluation / Observability / CI |
| H | 23-24 | Productization / Portfolio |

## 设计原则

- 学习优先：每个模块都要能解释直觉、原理、调用链和边界。
- 测试优先：核心模块必须配套单元测试、集成测试和回归测试。
- 本地优先：早期不依赖真实 API，使用 mock LLM 保持可重复。
- 安全优先：文件和命令执行必须限制在授权工作区内，并逐步接入权限审批。
- 工业级优先：每个阶段都要说明已覆盖边界和仍缺能力。
- 文档诚实：README 和架构图必须反映真实已实现状态。

## 仓库地址

GitHub: <https://github.com/nanhanq1/personal-coding-assistant.git>
