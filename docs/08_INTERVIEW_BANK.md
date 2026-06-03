# Interview Bank

## Agent Loop

### 1. 什么是 Agent Loop？

Agent Loop 是让 LLM、工具执行和上下文历史形成闭环的控制结构。它不是一次性调用模型，而是让模型根据历史决定是否调用工具，再把工具结果写回历史，让模型继续生成最终答案。

### 2. 为什么 Coding Agent 不能只调用一次 LLM？

因为真实代码任务需要读取文件、搜索代码、运行测试、查看错误、再修复。一次性 LLM 调用无法获得执行环境里的新信息，也无法验证自己的修改。

### 3. mock LLM 在项目早期有什么价值？

mock LLM 让我们稳定复现 tool call 和 final answer，从而先测试 Agent Loop 控制流。它避免真实模型的不确定性、网络问题和 API 成本干扰架构学习。

## 今日检查问题

1. 为什么工具结果要作为新的 message 写回 history，而不是直接存在局部变量里？
2. Agent Loop 什么时候应该停止？
3. 如果 LLM 请求一个不存在的工具，Agent Loop 应该怎么处理？
4. 为什么今天先用 mock LLM，不直接接入真实 API？
5. `tool_call -> tool_result -> continue` 这个链路和 ReAct 有什么关系？

## Tool System

### 1. 为什么 Agent 不能长期依赖 `dict[str, callable]` 管理工具？

因为这种方式只能跑通最小 Demo，缺少工具描述、统一注册入口、参数约束、错误处理和权限扩展点。工具数量增加后，Agent Loop 会被具体工具细节污染，不利于后续接入文件工具、shell 工具、权限系统和 MCP。

### 2. `ToolCall`、`Tool`、`ToolRegistry` 和 `AgentLoop` 的职责分别是什么？

`ToolCall` 是 LLM 发出的结构化调用意图；`Tool` 是程序侧对真实工具函数的包装；`ToolRegistry` 是工具注册、查找和执行的统一路由；`AgentLoop` 只负责控制消息循环，把 tool call 交给 registry 执行，并把结果写回 history。

### 3. Day 2 的 `ToolRegistry` 距离工业级工具系统还缺什么？

还缺参数 schema 校验、权限审批、危险工具拦截、超时重试、异步执行、执行日志、trace、结构化错误、工具版本管理和 MCP 工具桥接。
