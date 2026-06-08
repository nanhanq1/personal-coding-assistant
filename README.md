# Personal Coding Assistant

一个学习优先、工程实践驱动的 Personal Coding Assistant Agent 项目。

本项目的目标不是快速拼装 Demo，而是从零实现 Coding Agent 的核心机制，并逐步演进到可以放入作品集和面试讲解的工业级雏形。当前阶段优先使用 mock LLM，先把 Agent Loop、工具调用、文件工具、shell runtime、测试和安全边界打牢，再逐步接入真实模型、RAG、MCP、Memory、权限系统和可观测性。

## 当前进度

- 路线阶段：12 周学习路线，第 1 周 Day 7。
- 当前主题：Agent Loop 与 Tool Routing 闭环。
- 当前状态：已完成 `user -> LLM -> tool_call -> tool_result -> LLM -> final_answer` 的最小可运行链路，并完成第 1 周周复盘和小范围边界重构。
- 已实现能力：
  - 标准 message schema：`Message`、`ToolCall`。
  - 可脚本化 mock LLM：`ScriptedLLM`。
  - 最小 Agent Loop：调用 LLM、执行工具、写回工具结果、继续循环。
  - 工具抽象：`Tool` 与 `ToolRegistry`。
  - 文件工具：`read_file`、`write_file`。
  - shell runtime：`run_command`，返回 `stdout`、`stderr`、`returncode`、`timed_out`、`duration_ms`。
  - 默认 coding 工具注册表：`create_coding_tool_registry()`。
  - 工作区路径边界校验、基础参数校验和工具错误回写。
  - pytest 单元测试、集成测试和示例脚本。

下一步将进入第 2 周：继续深化 Tool System，优先从工具参数 schema、`edit_file` 和更清晰的工具结果结构开始规划。

## 核心架构

### Agent 执行闭环

```mermaid
flowchart TD
    A["User request"] --> B["AgentLoop.run"]
    B --> C["Append user Message"]
    C --> D["LLM.complete(messages)"]
    D --> E{"Assistant has tool_calls?"}
    E -- "No" --> F["Return final answer"]
    E -- "Yes" --> G["Run each ToolCall"]
    G --> H["Append role=tool Message"]
    H --> D
```

这条链路回答的是：Agent 为什么不是只调用一次 LLM。模型先提出工具调用意图，程序执行真实工具，再把结果写回 `message history`，让模型基于新事实继续回答。

### 工具路由链路

```mermaid
flowchart LR
    A["ToolCall name + arguments"] --> B["ToolRegistry.run"]
    B --> C["Tool.run"]
    C --> D{"Tool type"}
    D --> E["ReadFileTool / WriteFileTool"]
    D --> F["ShellCommandTool"]
    E --> G["File system inside workspace_root"]
    F --> H["ShellRuntime"]
    H --> I["subprocess.run inside workspace_root"]
    G --> J["Tool result"]
    I --> J
```

这条链路回答的是：`AgentLoop` 为什么不直接 import 具体工具类。循环层只负责调度，注册表负责路由，工具层负责包装，runtime/handler 负责真实执行和安全边界。

## 项目结构

```text
.
├── docs/                 # 学习路线、任务、架构决策、实现日志和面试题归档
├── examples/             # 可直接运行的示例脚本
├── src/pca/              # Personal Coding Assistant 核心源码
│   ├── core/             # Agent Loop、Message、Mock LLM
│   ├── runtime/          # shell runtime、workspace、checkpoint 等运行层能力
│   └── tools/            # Tool 抽象、注册表、文件工具、shell 工具
├── tests/                # pytest 单元测试
├── AGENTS.md             # 本项目 Codex 工作规则
├── pyproject.toml        # Python 项目配置
└── README.md
```

## 环境要求

- Python 3.11+
- Windows / PowerShell 优先验证
- pytest

安装测试依赖：

```powershell
python -m pip install pytest
```

## 运行测试

```powershell
python -m pytest -q
```

当前最近一次全量验证基线：

```text
68 passed, 1 skipped
```

## 运行示例

```powershell
python examples/01_minimal_agent.py
```

期望看到类似输出：

```text
user -> assistant -> tool:echo -> assistant
```

## 面试讲解要点

如果面试官问“你这个 Agent 当前实现了什么”，可以这样回答：

> 当前版本实现了一个最小 Coding Agent harness。它有标准 message history、mock LLM、AgentLoop、ToolRegistry、文件工具和 shell runtime。一次任务会从用户消息进入 `AgentLoop`，LLM 如果返回 `ToolCall`，循环会通过 `ToolRegistry` 找到对应工具执行，并把工具结果作为 `role=tool` 的消息写回 history，随后再次调用 LLM，直到得到没有工具调用的最终回答。

如果面试官问“你怎么考虑安全边界”，可以这样回答：

> 当前阶段最重要的安全边界是 `workspace_root`。文件工具和 shell runtime 都会把用户或 LLM 给出的路径解析到授权工作区内，拒绝越界路径；shell runtime 还限制超时时间，并结构化返回 stdout、stderr、退出码和超时状态。不过这还不是完整安全系统，后续仍要补权限审批、危险命令分类、审计日志、sandbox、checkpoint 和 rollback。

## 设计原则

- 学习优先：每个模块都要能解释直觉、原理、调用链和边界。
- 测试优先：核心模块必须配套单元测试。
- 本地优先：初期不依赖真实 API，使用 mock LLM 降低不确定性。
- 安全优先：文件和命令执行必须限制在 `workspace_root` 内。
- 可演进：先做最小闭环，再逐步扩展权限、上下文、MCP、Memory 和可观测性。

## 学习路线

完整路线见：

- `docs/01_LEARNING_ROADMAP.md`
- `docs/02_DAILY_TASKS.md`
- `docs/05_LEARNING_NOTES.md`
- `docs/09_NEXT_ACTIONS.md`

当前 12 周主题包括：

1. Agent Loop
2. Tool System
3. Permission System
4. Planning / Todo
5. Context Engineering
6. Context Compression / RAG
7. Runtime / Sandbox
8. MCP
9. Memory
10. Graph / State Machine
11. Observability / Evaluation
12. Final Project

## 仓库地址

GitHub: <https://github.com/nanhanq1/personal-coding-assistant.git>
