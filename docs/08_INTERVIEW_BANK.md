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

