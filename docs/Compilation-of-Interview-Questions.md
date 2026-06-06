# Compilation of Interview Questions

本文件用于按天汇总 Personal Coding Assistant Agent 学习过程中的面试题、用户回答和标准回答。

## 记录规则

- 每完成一天的任务和要求后，追加当天面试题。
- 标题格式：`## 第 N 天：YYYY-MM-DD`。
- 每道题必须包含：面试题、用户回答、标准回答。
- 如果用户当天尚未回答，`用户回答` 先写“待补充”；用户回答后再补全。

## 模板

```markdown
## 第 N 天：YYYY-MM-DD

### 面试题 1：题目

- 用户回答：待补充
- 标准回答：

### 面试题 2：题目

- 用户回答：待补充
- 标准回答：
```

## 第 1 天：2026-05-26

### 面试题 1：什么是 Agent Loop？

- 用户回答：根据 2026-05-31 学习验收记录整理：Agent Loop 是从用户输入开始，调用 LLM；如果 LLM 产生 `tool_call`，Agent 执行工具，把 `tool_result` 写回 message history；然后再次调用 LLM，直到得到最终回答。
- 标准回答：Agent Loop 是 Coding Agent 的核心控制循环。它把 `user message -> LLM -> assistant tool_call -> tool execution -> tool result message -> LLM -> final answer` 串成闭环。它的价值不只是“多调用几次模型”，而是让模型能根据外部工具返回的事实继续决策。

### 面试题 2：为什么 Coding Agent 不能只调用一次 LLM？

- 用户回答：根据记忆摘要和学习验收记录整理：一次调用无法处理真实任务中的工具执行、失败反馈和后续修正，需要多轮 `think -> act -> observe -> continue`。
- 标准回答：真实代码任务需要和环境交互：读取文件、搜索代码、运行测试、观察报错、修改代码、再次验证。一次 LLM 调用只能基于已有上下文直接生成文本，无法获得执行环境中的新事实，也无法根据工具结果修正下一步动作。Agent Loop 通过多轮“思考、行动、观察、继续”把模型推理和环境反馈连接起来。

### 面试题 3：mock LLM 在项目早期有什么价值？

- 用户回答：根据 2026-05-31 学习验收记录整理：mock LLM 可以排除真实 LLM 的随机性、网络和 API 干扰，让我们专注验证 Agent Loop 控制流。
- 标准回答：mock LLM 是 Agent Loop 的稳定测试替身。它能固定输出预设的 tool call 和 final answer，让测试可重复、成本可控，并避免 API key、网络、模型随机性、模型质量这些变量干扰。早期用 mock LLM 可以先验证架构和控制流，后续再把 LLM adapter 替换成真实模型。

## 第 2 天：2026-06-01

### 面试题 1：为什么 Agent 不能长期依赖 `dict[str, callable]` 管理工具？

- 用户回答：`dict[str, callable]` 对于工具的操作单一，而且会使 `AgentLoop` 臃肿。
- 标准回答：`dict[str, callable]` 能跑通最小 Demo，但缺少工具元数据、统一注册入口、参数约束、错误处理和扩展边界。随着工具变多，Agent Loop 会越来越依赖具体函数，导致工具描述、工具执行、未知工具处理、重复注册等逻辑分散。`ToolRegistry` 把这些能力集中起来，让 Agent Loop 只关心 `tool_call.name` 和 `tool_call.arguments`，更接近工业级工具路由结构。

### 面试题 2：`ToolCall`、`Tool`、`ToolRegistry` 和 `AgentLoop` 的职责分别是什么？

- 用户回答：`ToolCall` 封装 LLM 返回的工具信息，`Tool` 封装工具的注册信息，`ToolRegistry` 负责工具的注册，`AgentLoop` 封装 LLM 和工具的交互。调用链是 `AgentLoop -> ToolCall -> ToolRegistry -> Tool`。
- 标准回答：`ToolCall` 是 LLM 发出的结构化调用意图，表示“我要调用哪个工具、传什么参数”；`Tool` 是程序侧对真实工具函数的包装，保存工具名称、描述和 handler；`ToolRegistry` 是工具系统的路由表，负责注册、查找、执行和报错；`AgentLoop` 是控制循环，只负责把 LLM 的 tool call 交给 registry 执行，并把结果写回 message history。

### 面试题 3：Day 2 的 `ToolRegistry` 距离工业级工具系统还缺什么？

- 用户回答：缺少参数校验、错误处理以及安全权限。
- 标准回答：当前 `ToolRegistry` 只实现了最小的注册、查找、执行、注销和清空能力。它还缺少 JSON Schema 或 Pydantic 参数校验、权限审批、危险工具拦截、工具超时、重试、异步执行、工具执行日志、trace id、错误分类、返回值结构化、工具版本管理和 MCP 工具桥接。其中可观测性非常关键，因为 Agent 的问题不只来自代码 bug，还可能来自 LLM 幻觉、工具参数错误、权限限制、运行环境失败或工具超时。通过记录 `tool_name`、`arguments`、`result`、`error`、`duration_ms`、`trace_id` 等信息，我们才能判断问题发生在决策层、路由层、工具层还是环境层。没有这些记录，Agent 失败时只能看到“失败了”；有可观测性，才能复盘它调用了什么工具、传了什么参数、返回了什么结果、为什么失败，以及下一步应该重试、换工具、请求用户确认还是停止执行。这些能力会在后续文件工具、权限系统、runtime、observability 和 MCP 模块中逐步补齐。

## 第 3 天：2026-06-05

### 面试题 1：Coding Agent 为什么不能直接让 LLM 修改字符串，而需要文件工具？

- 用户回答：因为代码是以文件的形式保存的，LLM 可以操作字符串，但是要写回文件需要文件工具。LLM 可以给出写入的内容，但是不能直接将内容写入文件，而且有些文件的操作流程是固定的，如果让 LLM 进行给出，可能由于 LLM 的幻觉问题导致操作失败。
- 标准回答：LLM 本质上只生成文本，它可以提出“应该把某段内容改成什么”，但不能直接对磁盘文件产生副作用。代码库中的真实状态保存在文件系统里，Coding Agent 必须通过 `read_file`、`write_file`、后续的 `edit_file` 等工具，把模型的文本决策转换成可验证、可测试、可记录的文件操作。文件工具还能固定编码、路径解析、工作区边界、异常处理和审计流程，避免让 LLM 凭空描述操作步骤时因为幻觉、路径错误或格式错误导致修改失败。

### 面试题 2：`read_file` 工具的返回值为什么应该进入 message history？

- 用户回答：`read_file` 的返回值是作为 LLM 的上下文存在的，帮助 LLM 做出决策，并且可以当出现操作失误时回退到执行的状态。
- 标准回答：`read_file` 的返回值是 Agent 从外部环境获得的新事实。把它写入 message history 后，LLM 下一轮才能基于真实文件内容继续判断，而不是依赖猜测或过期上下文。message history 同时也是一条可回放的执行轨迹：它记录了模型为什么读文件、读到了什么、之后如何决策。严格说，回退文件状态通常需要 checkpoint、git diff 或 workspace snapshot；message history 本身更适合用于解释、复盘和重新推理，不等价于完整回滚机制。

### 面试题 3：文件工具为什么要限制 workspace 边界？

- 用户回答：保证 LLM 做出决策的行为的安全性。
- 标准回答：文件工具会读写真实磁盘，如果不限制 workspace 边界，LLM 一旦生成错误路径、恶意路径或被提示注入诱导，就可能读取隐私文件、覆盖系统文件、污染无关项目，甚至破坏运行环境。`workspace_root` 的作用是把工具能力限制在当前授权项目目录内：相对路径必须解析到 workspace 内，绝对路径也必须仍然位于 workspace 内。这样后续才能进一步接入权限审批、审计日志、危险操作拦截和回滚机制。

### 面试题 4：`ToolCall` 和真正执行 `read_file()` 有什么区别？

- 用户回答：`ToolCall` 只是 LLM 根据上下文信息做出工具的封装，`read_file` 才是真正执行文件操作的工具函数。
- 标准回答：`ToolCall` 是 LLM 输出的结构化调用意图，表达“我想调用哪个工具、传入哪些参数”，它本身不会产生任何副作用。真正执行发生在程序侧：`AgentLoop` 读取 `ToolCall`，把 `tool_call.name` 和 `tool_call.arguments` 交给 `ToolRegistry.run(...)`，registry 找到对应 `Tool`，再由 `Tool.run(...)` 调用 `read_file(arguments)`。因此调用链上有清晰分层：LLM 负责提出意图，Agent runtime 负责路由和执行，工具函数负责接触真实环境并返回结果。
