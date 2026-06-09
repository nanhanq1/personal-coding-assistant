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

## 第 4 天：2026-06-07

### 面试题 1：为什么 shell runtime 比 `read_file` / `write_file` 更危险？

- 用户回答：因为 shell runtime 几乎可以操纵本机的所有文件和程序，如果没有管控，容易执行危险命令。
- 标准回答：文件工具主要读写指定文件，而 shell runtime 可以启动任意程序、访问环境变量、读写大量文件、安装依赖、删除文件、启动后台进程或长时间占用资源。它的影响范围不只是一两个文件，而是整个运行环境。因此 shell runtime 必须比文件工具更早接入工作目录边界、超时、权限审批、危险命令检测、审计日志和 sandbox 隔离。

### 面试题 2：为什么相对 `cwd` 必须以 `workspace_root` 为基准解析？

- 用户回答：因为 workspace 规定了程序或者命令运行的空间范围。
- 标准回答：`workspace_root` 是当前授权给 Agent 操作的项目边界。相对 `cwd` 如果按当前进程目录解析，就会受启动位置影响，可能在错误目录执行命令；如果按 `workspace_root` 解析，就能让 `cwd="."`、`cwd="src"` 等参数始终落在授权工作区内。解析后还必须检查最终路径是否仍在 `workspace_root` 内，防止 `..` 或绝对路径绕过边界。

### 面试题 3：`stdout`、`stderr`、`returncode`、`timed_out`、`duration_ms` 分别有什么作用？

- 用户回答：`stdout` 捕获子进程的输出；`stderr` 捕获子进程的错误；`returncode` 表示子进程命令是否执行成功；`timed_out` 表示子进程是否超时；`duration_ms` 表示子进程运行命令的时间。
- 标准回答：`stdout` 保存命令的正常输出，例如测试结果、打印内容或查询结果；`stderr` 保存错误输出，例如语法错误、依赖缺失或命令报错；`returncode` 是进程退出码，通常 `0` 表示成功，非 `0` 表示命令失败；`timed_out` 明确区分“命令自己失败”和“命令被 runtime 超时终止”；`duration_ms` 是可观测性字段，帮助判断命令耗时、定位慢命令，并为后续审计日志和性能分析提供依据。Agent 应该把这些字段写回 message history，让 LLM 能基于真实执行结果继续决策。

### 面试题 4：为什么 `ShellCommandTool` 不应该直接写一堆 `subprocess.run(...)` 逻辑，而要转发给 `ShellRuntime`？

- 用户回答：`ShellCommandTool` 类的职责是将命令工具封装成 `Tool` 类，而真正的实现逻辑应该放在 `ShellRuntime` 类中，面向对象编程。
- 标准回答：更准确地说，这是职责分离，不只是“面向对象”。`ShellCommandTool` 属于工具层，负责工具名称、描述、handler 和 `ToolRegistry` 集成；`ShellRuntime` 属于运行环境层，负责命令执行、工作目录解析、超时、环境变量、输出捕获和耗时统计。这样做的价值是：`AgentLoop` 和 `ToolRegistry` 不需要知道命令如何执行；未来如果把本地 subprocess 替换成 Docker、sandbox、远程执行器或带审批的 runtime，只需要替换 runtime 层，而不用重写工具路由和 Agent Loop。

### 面试题 5：现在这个 shell runtime 还不能算真正安全，至少还缺哪些工业级能力？

- 用户回答：我认为是一些适配能力，比如：如果我操作的 `cwd` 不在 workspace 范围内，但是又是完成任务所必须的；`command` 参数没做规范化处理，官方文档中说明了 `command` 最好是命令列表，比如 `["python", "-c", "import time; time.sleep(100)"]`，而不是字符串。至于其他方面还没有想到，因为已经有了参数校验。
- 标准回答：你指出的 `command` 列表形式是重要增强点，因为列表参数配合 `shell=False` 可以减少 shell 字符串解析和注入风险。`cwd` 超出 workspace 但任务必须完成时，不能直接绕过边界，而应该进入权限审批、扩大授权 workspace，或由用户显式确认新的工作目录。除此之外，工业级 shell runtime 还缺少危险命令分类、人工审批、命令 allowlist / denylist、审计日志、trace id、进程树清理、输出大小限制、环境变量脱敏、资源限制、sandbox / Docker 隔离、checkpoint / rollback、并发控制和更细粒度的权限策略。参数校验只是第一层安全边界，不等于完整安全。

## 第 5 天：2026-06-08

### 面试题 1：为什么 Day 5 要新增 `create_coding_tool_registry()`，而不是让 `AgentLoop` 直接 import `ReadFileTool`、`WriteFileTool` 和 `ShellCommandTool`？

- 用户回答：因为需要一个工具的统一的注册接口，有助于统一管理和分发以及区分。
- 标准回答：`create_coding_tool_registry()` 是内置 coding 工具的组合入口。它把 `ReadFileTool`、`WriteFileTool` 和 `ShellCommandTool` 注册到同一个 `ToolRegistry`，让 `AgentLoop` 只依赖统一的工具路由接口，而不是直接依赖具体工具类。这样可以保持职责分离：`AgentLoop` 负责循环和消息轨迹，`ToolRegistry` 负责查找和分发，具体工具负责真实执行和安全边界。后续新增、替换或禁用工具时，优先改注册入口，而不是改 Agent 主循环。

### 面试题 2：在 `write_file -> read_file -> final answer` 这个测试里，为什么 `write_file` 返回的 `"ok"` 必须写回 `message history`？

- 用户回答：因为根本原因是工具的调用结果是 context，有助于帮助 LLM 做出当前情形下的决策。
- 标准回答：工具结果就是 Agent 从外部环境获得的新上下文。`write_file` 返回 `"ok"` 表示写入动作已经成功完成；把它写回 `message history` 后，LLM 下一轮才能知道“文件已经写好”，从而安全地继续发起 `read_file`。如果不写回 history，LLM 只能猜测工具是否成功，可能重复写入、跳过验证，或者基于错误状态继续回答。message history 同时也是可回放轨迹，能解释 Agent 为什么进入下一步。

### 面试题 3：`ToolCall` 和真正执行工具有什么区别？请用 `ToolCall(name="read_file", arguments={...})` 举例说明。

- 用户回答：`ToolCall` 只是将 LLM 的返回结果进行了封装，就是告诉你工具的名称是什么以及工具所需的参数，然后通过统一的工具注册入口进行分发。
- 标准回答：`ToolCall(name="read_file", arguments={...})` 是 LLM 发出的结构化调用意图，表示“我想读取某个文件，并且这些是参数”。它本身不会读取磁盘，也不会产生副作用。真正执行发生在程序侧：`AgentLoop` 读取 `tool_call.name` 和 `tool_call.arguments`，交给 `ToolRegistry.run(...)`；registry 找到名为 `read_file` 的 `Tool`；`Tool.run(arguments)` 再调用 `ReadFileTool` 的 handler；最后文件工具解析路径、检查 `workspace_root` 并读取文件内容。LLM 提出意图，runtime 负责执行，这是工具调用体系的核心分层。

### 面试题 4：如果 `read_file` 读取失败，为什么更好的做法是把错误作为 tool message 写回 history，而不是直接让整个 AgentLoop 崩掉？

- 用户回答：因为工具调用失败的原因有很多种，比如环境问题、网络问题、以及本身工具的问题，你不能保证哪种问题，所以要求将工具调用失败的结果进行返还到 history，让 LLM 根据上下文进行判断和决策，比如换个工具或者继续这个工具以及跳过这个决策路径换个路径。
- 标准回答：工具失败也是一种环境反馈。失败原因可能是路径不存在、参数错误、权限不足、工作区越界、文件被占用或工具自身 bug。如果 AgentLoop 直接崩掉，轨迹会中断，LLM 没有机会理解失败原因，也不能改用其他策略。把错误作为 `role="tool"` 的消息写回 history 后，LLM 可以根据错误决定重试、换路径、请求用户确认、调用别的工具或停止执行并解释问题。工业级 Agent 需要可恢复和可复盘，而不是遇到一次工具错误就丢失上下文。

### 面试题 5：当前 Day 5 代码离工业级 Coding Agent 还缺哪三个关键能力？

- 用户回答：planner、危险工具和命令的分类和预防、上下文工程以及记忆系统。
- 标准回答：这些方向是正确的。当前 Day 5 仍处在第 1 周 Agent Loop 阶段，主要证明多工具可以通过统一注册表进入同一条循环链路。距离工业级 Coding Agent 至少还缺：第一，planner / todo 状态机，用于拆解任务、记录步骤和控制多轮执行；第二，权限系统和危险命令分类，用于在写文件、运行 shell、删除文件、安装依赖等高风险操作前进行风险评估和人工审批；第三，上下文工程和记忆系统，用于选择相关代码文件、压缩历史、检索长期偏好和任务经验。除此之外还需要结构化 tool result、schema 校验、可观测 trace、checkpoint / rollback、sandbox 和 MCP tool bridge。

## 第 6 天：2026-06-08

### 面试题 1：请用 30 秒解释当前 Personal Coding Assistant 已经实现了什么。

- 用户回答：实现了 `user -> LLM -> tool call -> tool registry -> tool run -> tool result -> LLM -> final answer` 的闭环，其中当前验证使用的是 mock LLM，并不是真实 LLM 环境。
- 标准回答：当前项目实现了一个最小 Coding Agent harness，包含 `Message` / `ToolCall`、mock LLM、`AgentLoop`、`ToolRegistry`、文件工具和 shell runtime。它能完成 `user -> LLM -> tool_call -> tool_result -> LLM -> final_answer` 的最小闭环，并通过测试验证工具调用结果会写回 message history。

### 面试题 2：`user -> LLM -> tool_call -> tool_result -> LLM -> final_answer` 和 `AgentLoop -> ToolRegistry -> Tool -> handler/runtime` 有什么区别？

- 用户回答：前面是 Agent Loop 的整体逻辑流程，后者是 Agent Loop 的实现和封装细节。
- 标准回答：前一条是 Agent 从用户请求到最终回答的业务执行闭环，强调 LLM、工具调用和工具结果如何交替推进；后一条是程序内部执行工具调用的工程路由链路，强调 `AgentLoop` 不直接依赖具体工具，而是通过 `ToolRegistry` 找到 `Tool`，再由 handler 或 runtime 执行真实副作用。

### 面试题 3：为什么 README 和架构图必须和真实代码保持一致？

- 用户回答：README 和架构图是外部读者理解项目的入口，也是面试时解释项目的依据。
- 标准回答：README 和架构图是外部读者理解项目的入口，也是面试时解释项目的依据。如果文档画的是未来设想、代码却没有实现，会误导读者，也会暴露工程表达不严谨。好的架构图应该反映当前真实调用链，并明确哪些能力已经实现、哪些只是后续计划。

### 面试题 4：当前项目的安全边界主要在哪里？还缺什么？

- 用户回答：当前主要安全边界是 `workspace_root`：文件工具和 shell runtime 都会把路径限制在授权工作区内，还缺权限审批、危险命令分类。
- 标准回答：当前主要安全边界是 `workspace_root`：文件工具和 shell runtime 都会把路径限制在授权工作区内；shell runtime 还会限制超时时间并结构化返回执行结果。但它还缺权限审批、危险命令分类、审计日志、输出大小限制、环境变量脱敏、sandbox、checkpoint / rollback 和进程树清理。

### 面试题 5：如果面试官问“为什么现在还不用真实 LLM”，应该怎么回答？

- 用户回答：重点是验证 Agent Loop 和工具路由控制流。真实 LLM 会带来 API key、网络、费用、随机性和输出不可控问题，容易干扰核心架构验证。
- 标准回答：第 1 周重点是验证 Agent Loop 和工具路由控制流。真实 LLM 会带来 API key、网络、费用、随机性和输出不可控问题，容易干扰核心架构验证。先用 `ScriptedLLM` 固定响应，可以让测试稳定复现 `tool_call -> tool_result -> final answer`，等控制流和安全边界打牢后再接真实模型 adapter。

## 第 7 天：2026-06-08

### 面试题 1：为什么 Day 7 不应该继续大规模新增功能？

- 用户回答：Day 7 是第 1 周收口日，目标是确认最小 Agent Loop、工具路由、测试和文档是否稳定。
- 标准回答：Day 7 是第 1 周收口日，目标是确认最小 Agent Loop、工具路由、测试和文档是否稳定，而不是提前进入 planner、权限系统、真实 LLM 或 RAG。大规模新增功能会模糊第 1 周的学习重点，也容易在基础边界还没完全讲清时引入复杂耦合。

### 面试题 2：为什么文件工具不能把 `path=123` 静默转成 `"123"`？

- 用户回答：工具参数来自 LLM 输出，不能默认可信。
- 标准回答：工具参数来自 LLM 输出，不能默认可信。如果把非字符串路径静默转成字符串，`read_file` 会把类型错误伪装成文件不存在，`write_file` 甚至可能创建意外文件。这会掩盖参数生成错误，也会让审计和错误恢复更困难。更好的做法是在工具边界明确拒绝非字符串 `path`。

### 面试题 3：这次 Day 7 的 RED 测试证明了什么？

- 用户回答：RED 测试证明当前代码确实存在目标缺口。
- 标准回答：RED 测试证明当前代码确实存在目标缺口：非字符串 `path` 没有在参数边界被拒绝。`read_file` 会继续尝试读取名为 `123` 的路径，`write_file` 会写出名为 `123` 的文件。看到测试按预期失败后，再做最小修复，才能确认测试不是装饰性覆盖，而是真的能抓住回归。

### 面试题 4：请分别解释 Agent 执行闭环和工具路由链路。

- 用户回答：Agent 执行闭环是 `user -> LLM -> tool_call -> tool_result -> LLM -> final_answer`，强调模型如何根据工具结果继续决策。工具路由链路是 `AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler/runtime`。
- 标准回答：Agent 执行闭环是 `user -> LLM -> tool_call -> tool_result -> LLM -> final_answer`，强调模型如何根据工具结果继续决策。工具路由链路是 `AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler/runtime`，强调程序内部如何把 LLM 的调用意图转成真实工具执行。前者是业务执行流程，后者是工程实现路径。

### 面试题 5：第 2 周深化 Tool System 时，最应该优先补哪些能力？

- 用户回答：工具参数 schema、结构化 tool result 和可观测字段，让工具成功、失败、耗时和错误原因可被 Agent 与测试稳定消费。
- 标准回答：优先补三类能力：第一，工具参数 schema，例如 JSON Schema 或 Pydantic，用来系统化约束工具输入；第二，`edit_file` 或 diff/patch 能力，避免长期依赖整文件覆盖；第三，结构化 tool result 和可观测字段，让工具成功、失败、耗时和错误原因可被 Agent 与测试稳定消费。权限审批和危险命令分类也很重要，但应在工具边界更清楚后继续推进。
