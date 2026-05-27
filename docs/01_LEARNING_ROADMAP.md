# Learning Roadmap

## 12 周路线

| 周次 | 主题 | 目标 | 核心产出 |
| --- | --- | --- | --- |
| 1 | Agent Loop | 实现最小 Agent 循环 | messages、mock LLM、tool call parser、loop runner、tests |
| 2 | Tool System | 实现工具注册、工具 schema、工具执行 | Tool 抽象、ToolRegistry、read_file、write_file、edit_file、run_bash |
| 3 | Permission System | 实现危险命令检测和人工审批 | risk classifier、permission policy、approval flow、audit log |
| 4 | Planning / Todo | 实现任务拆解和 Todo 管理 | planner、todo list、task state、checkpoint |
| 5 | Context Engineering | 实现 repo scanner、file summary、prompt builder | repo_map、file summaries、context selector、prompt builder |
| 6 | Context Compression / RAG | 实现上下文压缩和基础检索 | compressor、text splitter、embedding adapter mock、retriever |
| 7 | Runtime / Sandbox | 实现 workspace、shell runtime、checkpoint、rollback | workspace abstraction、shell runtime、git checkpoint、rollback |
| 8 | MCP | 实现最小 MCP client/server | MCP server skeleton、MCP client skeleton、tool bridge、example MCP tool |
| 9 | Memory | 实现长期记忆系统 | SQLite memory、task memory、preference memory、memory search |
| 10 | Graph / State Machine | 用 LangGraph 思想重构 Agent | state nodes、conditional edges、checkpoint、interrupt |
| 11 | Observability / Evaluation | 实现日志、trace、replay、评估 | tool call log、trace id、replay file、simple eval cases |
| 12 | Final Project | 整合项目 | CLI、README、examples、architecture document、interview explanation |

## 当前学习主线

第 1 阶段对标 learn-claude-code，先理解 Agent Harness 的核心骨架，再逐步扩展工具、权限、上下文和记忆。

## 第 1 周目标

实现最小 Agent Loop，让系统能够完成：

```text
user_message -> llm.complete -> assistant tool_call -> run tool -> tool_result -> llm.complete -> final_answer
```

