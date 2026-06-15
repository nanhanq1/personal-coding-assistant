# Learning Roadmap

## 路线定位

本路线的最终目标是完成一个**工业级 Personal Coding Assistant Agent 项目**，不是停留在 Demo。

路线采用“可运行垂直切片 -> 工业级补强 -> 系统集成”的方式推进：

- 每周先实现一个可验证的核心闭环，避免一开始堆大而空的架构。
- 每周必须同步补齐测试、错误边界、安全边界、文档、面试表达和工业级差异说明。
- 后续周会持续回到前面模块做加固，而不是把早期实现当成最终实现。
- “最小实现”只表示当天的学习切片足够小，不表示最终质量是 Demo。

## 工业级验收标准

每个模块完成时，默认至少满足以下验收标准：

1. 有清晰的调用链和模块边界。
2. 有 focused 单元测试或集成测试覆盖正常路径和关键失败路径。
3. 有输入校验、错误语义和安全边界说明。
4. 有文档记录当前实现、工业级差距和后续加固方向。
5. 有面试题回答与归档，确保用户能解释设计而不是只会运行代码。
6. 如果涉及执行、文件、命令、网络、凭据或外部工具，必须说明权限、审计、回滚或隔离策略的当前状态。

## 12 周路线

| 周次 | 主题 | 目标 | 核心产出 |
| --- | --- | --- | --- |
| 1 | Agent Loop | 建立可测试的 Agent 执行主循环 | messages、mock LLM、tool call parser、loop runner、tests、失败边界 |
| 2 | Tool System | 建立可扩展工具系统和结构化结果边界 | Tool 抽象、ToolRegistry、tool schema、read/write/edit/run_command、ToolResult、工具错误语义 |
| 3 | Permission System | 建立执行前风险分类、策略判断和人工审批骨架 | risk classifier、permission policy、approval flow、audit log、拒绝/审批测试 |
| 4 | Planning / Todo | 建立可恢复的任务拆解和 Todo 状态管理 | planner、todo list、task state、checkpoint、replanning、失败恢复 |
| 5 | Context Engineering | 建立代码库理解和上下文选择能力 | repo_map、file summaries、context selector、prompt builder、预算控制 |
| 6 | Context Compression / RAG | 建立上下文压缩、检索和引用能力 | compressor、text splitter、embedding adapter mock、retriever、rerank/citation 边界 |
| 7 | Runtime / Sandbox | 建立安全运行环境和回滚能力 | workspace abstraction、sandbox/runtime、git checkpoint、rollback、resource limit |
| 8 | MCP | 建立外部工具协议接入能力 | MCP server/client、tool bridge、resource/prompt bridge、权限边界 |
| 9 | Memory | 建立长期记忆和可审计记忆更新能力 | SQLite memory、task memory、preference memory、memory search、memory update policy |
| 10 | Graph / State Machine | 用状态机重构复杂 Agent 控制流 | state nodes、conditional edges、checkpoint、interrupt、human-in-the-loop |
| 11 | Observability / Evaluation | 建立可观测、可回放、可评估能力 | structured logs、trace id、tool call log、replay、eval cases、failure analysis |
| 12 | Final Project | 整合成可演示、可解释、可继续扩展的工业级项目 | CLI、README、examples、architecture document、interview explanation、portfolio write-up、end-to-end eval |

## 当前学习主线

第 1 阶段对标 learn-claude-code / Claude Code-like Agent Harness，先实现核心骨架；后续逐步吸收 mini-SWE-agent、OpenAI Agents SDK、Aider、Cline、OpenHands、LangGraph、MCP、Mem0/Letta/Graphiti/Zep、LlamaIndex 等主流项目的关键机制。

这不是只做 Demo，也不是照搬某一个开源项目。路线目标是把主流 Coding Agent / Agent Platform 的核心工程能力拆成 12 周可实现、可测试、可面试讲解的工业级项目模块。

## 当前路线状态

- 第 1 周 Agent Loop 已完成：已实现 `Message`、`ToolCall`、`ScriptedLLM`、`AgentLoop`、基础文件工具、shell runtime、默认工具注册表和最小示例。
- 第 2 周 Tool System 已收口：已实现 `ToolParameter`、工具 schema 导出、默认工具 schema 示例、`edit_file`、结构化 `ToolResult`、`AgentLoop._tool_result_to_message(...)`，并补强 `run_command.env` 敏感输出脱敏。
- 第 2 周 Day 7 面试题已完成回答、评审和归档；当前没有面试题门禁阻塞。
- 当前进入第 3 周 Day 1：Permission System 起步，重点是危险命令识别与最小权限策略。
- 最新已实现主线架构和工业级差异整理见 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`。

## 第 1 周目标

实现最小 Agent Loop，让系统能够完成：

```text
user_message -> llm.complete -> assistant tool_call -> run tool -> tool_result -> llm.complete -> final_answer
```

## 第 2 周目标状态

第 2 周目标已经完成并收口。当前工具系统已经具备：

- 工具参数 schema：`ToolParameter`、`Tool.to_schema()`。
- 工具事实源：`ToolRegistry.list_tool_schemas()`。
- 默认 coding 工具：`read_file`、`write_file`、`edit_file`、`run_command`。
- 局部编辑边界：`edit_file` 要求 `old_text` 非空且唯一出现。
- 结构化结果：`ToolRegistry.run(...) -> ToolResult`。
- AgentLoop 消费边界：`AgentLoop._tool_result_to_message(...)`。
- shell runtime 边界：`workspace_root`、`cwd`、timeout、env 基础校验和敏感输出脱敏。

第 2 周仍然不是完整权限系统。危险命令分类、人工审批、权限策略、审计日志、sandbox、checkpoint/rollback 属于第 3 周及后续任务。

## 第 3 周目标

第 3 周主题是 Permission System。当前 Day 1 做最小起步，但验收标准按工业级方向设计：

- 明确 Tool System 和 Permission System 的边界：Tool System 负责“怎么调用工具”，Permission System 负责“是否允许执行”。
- 设计最小风险分类：`safe`、`needs_approval`、`blocked`。
- 先实现危险命令识别或等价风险分类器。
- 暂不实现完整审批 UI、复杂 sandbox、checkpoint/rollback、真实 LLM adapter、RAG 或 MCP。
- 每个风险分类必须有测试和理由字段，为后续审批、审计日志和策略系统留下结构化边界。

## 最终工业级完成定义

第 12 周结束时，项目不应只是能跑通示例，而应至少具备：

- 一条可运行的端到端 Coding Agent 主链。
- 可配置的工具系统、权限系统、上下文系统、记忆系统和运行时边界。
- 对危险文件操作和危险命令有执行前控制。
- 对工具调用、审批、失败和恢复有可观测记录。
- 对核心模块有测试覆盖和回归示例。
- README、架构文档、ADR、学习笔记和面试讲解能准确反映真实能力。
- 明确列出仍未达到生产级平台的部分，例如多用户隔离、远程执行、企业级密钥管理、分布式 trace、完整 UI 等。
