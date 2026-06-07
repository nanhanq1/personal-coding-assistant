# Personal Coding Assistant

一个学习优先、工程实践驱动的 Personal Coding Assistant Agent 项目。

本项目的目标不是快速拼装一个 Demo，而是从零实现 Coding Agent 的核心机制，并逐步演进到可以放入作品集和面试讲解的工业级雏形。当前阶段优先使用 mock LLM，先把 Agent Loop、工具调用、文件工具、shell runtime、测试和安全边界打牢，再逐步接入真实模型、RAG、MCP、Memory、权限系统和可观测性。

## 当前进度

- 路线阶段：12 周学习路线，第 1 周。
- 当前主题：Agent Loop 与 Tool System。
- 已实现能力：
  - 标准 message schema。
  - mock LLM。
  - 最小 Agent Loop。
  - `Tool` 与 `ToolRegistry`。
  - 文件工具：`read_file`、`write_file`。
  - shell runtime 与 `run_command` 工具。
  - 工作区路径边界校验。
  - 单元测试与示例脚本。

下一步将进入 Day 5：整合 Loop + Tools，重点验证多个工具如何通过统一注册表被 Agent Loop 路由和执行。

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
65 passed, 1 skipped
```

## 运行示例

```powershell
python examples/01_minimal_agent.py
```

期望看到类似输出：

```text
user -> assistant -> tool:echo -> assistant
```

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
