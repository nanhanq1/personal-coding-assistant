# Compilation of Interview Questions

本文件用于按天汇总 Personal Coding Assistant Agent 学习过程中的已回答面试题、用户回答和标准回答。

## 记录规则

- 每完成一天的任务和要求后，先确认用户是否已经回答当天面试题。
- 只有用户已经回答后，才能追加当天面试题、用户回答和标准回答。
- 新增的已回答每日面试题记录必须写在本文档末尾；正常情况下后续天数递增，因此末尾追加后仍应保持从小到大的天数顺序。
- 标题格式：`## 第 N 天：YYYY-MM-DD`。
- 每道题必须包含：面试题、用户回答、标准回答。
- 如果用户尚未回答，不能把该题写入本文档，也不能使用占位回答；必须先把未回答题推送给用户，等用户回答后再整理归档。

## 模板

```markdown
## 第 N 天：YYYY-MM-DD

### 面试题 1：题目

- 用户回答：用户实际回答或基于用户原回答整理后的回答
- 标准回答：

### 面试题 2：题目

- 用户回答：用户实际回答或基于用户原回答整理后的回答
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

## 第 8 天：2026-06-09

### 面试题 1：`Tool schema` 解决的核心问题是什么？

- 用户回答：解决的核心问题是：将 LLM 的输出进行规范化，让 LLM 知道有什么参数、什么参数是必须的、参数类型以及其他的规范。
- 标准回答：`Tool schema` 解决的是工具调用契约问题。它把工具名、工具描述、参数名、参数类型、必填字段和参数说明结构化，让未来真实 LLM adapter 可以把工具列表提供给模型，也让程序在进入具体 handler 前做第一层参数校验。没有 schema 时，模型只能从自然语言描述里猜参数，容易生成错误字段、漏掉必填参数或传入错误类型。

### 面试题 2：为什么 `Tool schema` 不能替代 `workspace_root`、危险命令审批等安全校验？

- 用户回答：因为 `Tool schema` 主要的功能是进行参数类型的正确返回，以及给出什么参数是必须的、参数值的特定选择和参数的一些其他规范；但是一些参数的安全性检测并不能进行，这需要逻辑编码。`Tool schema` 只是参数的说明文档，并不能实现参数的逻辑性校验。
- 标准回答：这个方向正确。更工程化地说，schema 是工具调用的结构契约，只能表达字段是否存在、字段大致类型、字段说明和部分枚举约束。它不能判断路径解析后是否越过 `workspace_root`，不能判断 shell 命令是否危险，不能判断写文件是否需要审批，也不能处理 checkpoint、rollback、审计日志和用户授权。这些属于业务语义、安全策略和 runtime 逻辑，必须由具体工具、runtime 和后续 Permission System 实现。

### 面试题 3：为什么必填参数缺失要在 `Tool.run(...)` 里失败，而不是等具体 handler 失败？

- 用户回答：浪费时间，导致结果的滞后，并且如果传入具体的 handler，你并不能清楚 handler 在校验参数之前有什么逻辑。
- 标准回答：`Tool.run(...)` 是所有工具执行的统一入口，把通用参数校验放在这里可以让错误更早、更一致地暴露。如果缺少 `path`、`command` 这类必填参数还进入 handler，不同工具可能抛出不同异常，甚至产生副作用。前置校验能保证 handler 只处理已经满足基础契约的参数，让具体工具专注业务语义和安全边界。

### 面试题 4：`ToolRegistry.list_tool_schemas()` 未来会被真实 LLM adapter 如何使用？

- 用户回答：会传给 LLM 工具的名称和描述，帮助 LLM 决定调用什么工具。
- 标准回答：真实 LLM adapter 在调用模型前，可以从 `ToolRegistry.list_tool_schemas()` 拿到当前可用工具列表，并把这些 schema 传给模型。模型根据工具名、描述和参数 schema 决定是否调用工具、调用哪个工具、生成哪些 arguments。这样工具注册表就不只是执行路由表，也是模型可用工具能力的统一来源。

### 面试题 5：当前第 2 周 Day 1 的 schema 实现还缺哪些工业级能力？

- 用户回答：兜底措施，其实我感觉已经足够成熟了。
- 标准回答：当前实现只覆盖基础参数声明和简单类型校验，仍缺少完整 JSON Schema 校验、枚举值、字符串长度、数组元素类型、对象内部结构、默认值、参数示例、schema 版本管理、工具权限元数据、可观测字段、结构化 tool result，以及与真实 OpenAI / Anthropic adapter 的格式转换。权限审批和危险命令分类也还没有实现，后续应在 Permission System 中补齐。

## 第 9 天：2026-06-11

### 面试题 1：为什么 `list_tool_schemas()` 应该从 `ToolRegistry` 导出，而不是在 OpenAI adapter 里手写？

- 用户回答：因为 `list_tool_schemas()` 是将工具转换为 JSON Schema，`ToolRegistry` 存在 Tools，可以直接进行转换，但是 OpenAI adapter 是对于原始的 JSON Schema 进行修改。
- 标准回答：方向正确。更工程化地说，`ToolRegistry` 是当前可用工具的唯一事实源，它知道真实注册了哪些 `Tool`。`list_tool_schemas()` 从 registry 导出，可以保证“程序能执行的工具”和“模型看到的工具列表”一致。OpenAI adapter 不应该手写工具清单，否则未来新增、删除或修改工具时容易和注册表脱节。adapter 的职责应该是格式转换：把项目内部中立 schema 转成 OpenAI、Anthropic 或其他模型 API 需要的外部格式。

### 面试题 2：为什么当前项目内部 schema 不应该一开始绑定某一家模型 API？

- 用户回答：因为要有通用性，可以适配不同的模型，毕竟不同的模型在不同的方向的能力上是不同的。
- 标准回答：这个回答抓住了通用性。更完整地说，内部 schema 是项目自己的工具契约，应该先稳定表达工具名、描述、参数和必填字段；不同模型厂商对工具字段命名、strict mode、参数格式和返回 tool call 的结构可能不同。如果内部 schema 一开始绑定 OpenAI 格式，后续接 Anthropic、本地模型或 MCP bridge 时就会把 vendor 细节扩散到工具系统。更好的边界是：工具系统输出中立 schema，adapter 层负责厂商格式转换。

### 面试题 3：`additionalProperties: True` 和 OpenAI strict schema 的 `additionalProperties: false` 有什么差别？

- 用户回答：值为 True 表示可以允许 LLM 传入的参数不在工具参数集合的范围内，False 就是强制 LLM 模型返回的参数必须只包含工具参数的集合。
- 标准回答：基本正确。`additionalProperties: True` 表示 schema 层不禁止额外字段；这适合当前项目 Day 1 的宽松阶段，因为我们还没有完整 JSON Schema 校验器，也没有在 `Tool.run(...)` 中拒绝额外字段。`additionalProperties: false` 表示对象只能包含 `properties` 中声明的字段，常用于更严格的 tool schema。需要注意：schema 写成 false 只是契约的一部分，程序侧也要有相应校验或依赖模型 API 的 strict 约束，否则就会出现“文档说禁止，但 runtime 仍接受”的契约漂移。

## 第 10 天：2026-06-11

### 面试题 1：为什么工具描述质量会影响模型选工具？

- 用户回答：工具的描述表现了一个工具的功能、应用场景、工具的边界和与其他工具的调用顺序的关系，这些决定了 LLM 应该在什么流程中的什么节点调用工具。
- 标准回答：方向正确。工具描述是模型在调用工具前能看到的能力说明，它会影响模型判断“是否需要工具、调用哪个工具、什么时候调用、调用后期待什么结果”。高质量描述要说明功能、适用场景、副作用、安全边界、调用顺序和返回语义。描述过短或边界不清时，模型更容易把读工具当写工具、把命令执行当文件编辑，或者在不合适的流程节点调用工具。

### 面试题 2：`read_file` 和 `write_file` 的描述为什么必须明确“只读”和“写入或覆盖”？

- 用户回答：表明了工具的功能边界，让 LLM 在决定写的时候不会调用读工具。
- 标准回答：正确。`read_file` 和 `write_file` 的核心差别是副作用边界：`read_file` 只观察环境，不修改磁盘；`write_file` 会写入或覆盖真实文件。描述中明确“只读”和“写入或覆盖”，可以帮助模型区分观察动作和修改动作，避免在需要查看文件时误写文件，也避免在需要修改文件时误以为读取工具能产生副作用。这个边界也是后续权限审批、审计日志和风险分类的基础。

### 面试题 3：为什么 `run_command` 的描述必须写清楚 `workspace_root`、`timeout_seconds` 和返回字段？

- 用户回答：说明工具的应用环境，避免后面的字段检查失败。至于为什么说明返回字段，我也不清楚，毕竟我认为描述就是让 LLM 知道在合适的地方调用正确的工具；至于工具的返回值，这是工具的实现问题，只作为后续 LLM 的判断决策的一个依据。
- 标准回答：前半部分方向对，但要补强：`workspace_root` 和 `timeout_seconds` 不只是为了避免字段检查失败，它们是命令执行工具的安全和运行契约。`workspace_root` 告诉模型命令只能在授权工作区内运行，`timeout_seconds` 告诉模型这个工具必须有超时边界，不能默认无限执行。返回字段也不是纯实现细节；对 LLM 来说，`stdout`、`stderr`、`returncode`、`timed_out` 是调用前的能力承诺，也是调用后的观察格式。模型调用前要知道这个工具能返回哪些执行信号，调用后才能判断命令成功、失败、报错还是超时，并决定下一步是重试、修复代码、换命令还是停止。

## 第 11 天：2026-06-11

### 面试题 1：为什么 `edit_file` 不应该默认替换所有匹配到的 `old_text`？

- 用户回答：容易出现逻辑错误，比如：`old_text` 在文件中多处存在，但是每次存在在整体结构代码中的逻辑不一样，如果全部替换为 `new_text` 可能导致逻辑错误。
- 标准回答：这是正确方向。同一段文本在不同函数、不同分支、不同测试或不同注释里可能有完全不同的语义。`edit_file` 如果默认全部替换，LLM 一次不精确的调用就可能同时改坏多个位置。Day 3 的安全策略是：`old_text` 必须在文件中唯一出现；如果出现 0 次说明上下文过期，如果出现多次说明编辑意图不够精确，两种情况都应该失败而不是猜测。

### 面试题 2：为什么 `old_text` 为空必须拒绝？

- 用户回答：`old_text` 为空表示 LLM 认为此文件不需要 edit 但是调用了此函数，逻辑错误，所以要拦截，避免不必要的修改。
- 标准回答：你说对了“这是工具调用逻辑错误，需要拦截”，还要补一个更底层的 Python 字符串风险：空字符串会匹配到每个字符之间的位置。也就是说，如果允许 `old_text=""`，替换逻辑可能把 `new_text` 插入到文件的很多位置，造成灾难性写入。因此 `old_text` 必须是非空字符串；而 `new_text` 可以为空字符串，因为删除一段明确文本是合法编辑。

### 面试题 3：`edit_file` 和 `write_file` 分别适合什么场景？

- 用户回答：`edit_file` 适合修改文件的部分代码，比如替换或者追加代码；`write_file` 适合对已有文件的代码进行整体性的重写或者新建一个新的文件代码进行编写。
- 标准回答：总体正确。更精确地说，当前 Day 3 的 `edit_file` 只实现“在已有文件中替换一段明确且唯一的文本”，适合小范围局部修改；追加代码可以在未来作为更高级编辑能力实现，但当前不默认支持。`write_file` 适合新建文件、生成完整文件或明确需要整文件覆盖的场景。两者都可能产生真实文件副作用，因此都必须保留 `workspace_root` 边界和参数校验。

## 第 12 天：2026-06-12

### 面试题 1：为什么工具结果不能长期只靠字符串和异常表达？

- 用户回答：因为当工具出现错误时，不能定位错误的位置或者是哪次调用的工具出现了错误，以及日志。
- 标准回答：字符串和异常可以跑通最小 Demo，但缺少稳定字段。成功时字符串 `"ok"`、文件内容、shell dict 混在一起，失败时异常又被拼成文本，后续 LLM adapter、测试、日志和错误恢复都很难统一判断状态。结构化 `ToolResult` 把 `ok`、`result`、`error_type`、`error_message` 和 `duration_ms` 固定下来，让调用方能稳定区分成功、失败、错误类型和耗时。

### 面试题 2：为什么本次选择在 `ToolRegistry.run(...)` 边界返回 `ToolResult`，而不是立刻改 `Tool.run(...)`？

- 用户回答：因为 `Tool.run()` 是返回工具执行之后的结果，`ToolRegistry` 主要的作用就是规范工具调用以及充当工具的工厂。
- 标准回答：`ToolRegistry.run(...)` 是 `AgentLoop` 面向工具系统的统一入口，适合先作为结构化结果边界。`Tool.run(...)` 更靠近具体工具低层执行，当前文件工具和 shell runtime 的单元测试还依赖它保留原始返回值和异常语义。先在 registry 边界包装 `ToolResult`，可以让 AgentLoop 获得结构化结果，同时避免一次性重写所有具体工具测试和低层 API。

### 面试题 3：`ToolResult.ok`、`result`、`error_type`、`error_message`、`duration_ms` 分别解决什么问题？

- 用户回答：`ok` 表示工具是否成功，`result` 表示工具成功时的返回结果，`error_type` 表示工具调用错误时的错误类型，`error_message` 表示工具报错的信息，`duration_ms` 表示工具执行的时间。
- 标准回答：`ok` 表示一次工具调用是否成功；`result` 保存成功时的原始返回值；`error_type` 保存失败的异常类型，方便分类；`error_message` 保存具体错误信息，方便恢复和解释；`duration_ms` 保存执行耗时，方便可观测性、性能分析和后续 trace。它们合起来把一次工具执行从“模糊文本”变成“可测试的结果信封”。

### 面试题 4：为什么 `ToolResult` 不能替代权限系统、workspace 边界或 shell sandbox？

- 用户回答：`ToolResult` 只是表示由于参数类型、工作区间、JSON Schema、危险命令以及权限和沙箱造成的错误的表现，并不能代表他们的功能。
- 标准回答：`ToolResult` 只描述一次工具执行已经发生后的结果，不负责决定这个工具是否应该被允许执行。权限审批、危险命令分类、`workspace_root` 路径边界、shell sandbox、checkpoint 和 rollback 都属于执行前或执行中的安全策略。结构化结果能帮助记录和恢复，但不能替代安全控制本身。

### 面试题 5：当前最小 `ToolResult` 距离工业级工具结果还缺什么？

- 用户回答：不能表示工具的分类、工具名称、`agent_loop` 的循环次数、具体情况的错误类型标识。
- 标准回答：当前实现只是最小结果信封，还缺少 trace id、工具名、参数摘要、错误分类枚举、输出截断标记、重试建议、权限审批结果、结构化 JSON 序列化、审计日志持久化，以及和真实 LLM adapter 的 tool message 格式适配。后续 Day 5 可以先让 AgentLoop 更明确地消费 `ToolResult`，再逐步扩展 observability 和 permission metadata。

## 第 13 天：2026-06-13

### 面试题 1：Day 5 为什么不是重新设计 `ToolResult`，而是让 `AgentLoop` 明确消费它？

- 用户回答：先用最小测试跑通，主要增添或修改的内容。
- 标准回答：Day 4 已经完成了最小 `ToolResult`，并且 `ToolRegistry.run(...)` 已经会返回结构化结果。Day 5 的重点不是重新设计结果对象，而是补齐调用链上的消费边界：`AgentLoop` 应该明确知道工具系统返回的是 `ToolResult`，并把它转换成 LLM 能继续读取的 `role="tool"` 消息。这样可以用最小测试证明 `schema -> edit_file -> ToolResult -> tool Message -> LLM continue` 跑通，同时避免过早重构 `ToolResult` 字段、真实 adapter、trace 或权限系统。

### 面试题 2：schema、`edit_file` 和 `ToolResult` 在同一条工具链路中分别解决什么问题？

- 用户回答：Schema 主要的作用就是让模型知道工具的功能、边界以及参数限制，并可以规范模型的定义以及进行后续工具参数的校验；`edit_file` 就是对已有的文件中的特定的内容进行修改覆盖；`ToolResult` 就是统一格式封装工具调用的情况，还可以用于后续日志以及定位错误的位置，用于后续 LLM adapter 对各种模型厂商的不同的规范的实现。
- 标准回答：整体方向正确。schema 解决工具调用前的契约问题，让模型知道工具名、用途、边界、参数名、类型和必填字段，也让 `Tool.run(...)` 能在进入具体工具前做基础校验。`edit_file` 解决具体能力问题：在已有文件中把唯一出现的 `old_text` 精确替换成 `new_text`，并继续受 `workspace_root` 约束；它不是整文件覆盖工具。`ToolResult` 解决工具执行后的结果表达问题，用统一结构表达成功、失败、错误类型、错误消息和耗时，方便测试、日志、错误恢复和未来 adapter 序列化。

### 面试题 3：为什么 `edit_file` 失败时要写回 tool message，而不是直接让 AgentLoop 抛异常结束？

- 用户回答：因为 `edit_file` 的失败情况可能是由于 LLM 的幻觉或者 attention 机制导致的，将错误返回有利于 LLM 根据错误做出决策，比如是传入的参数错误还是网络问题或者权限问题，后续可能会人工介入。
- 标准回答：方向正确。`edit_file` 失败常见原因是上下文过期、`old_text` 不存在、`old_text` 出现多次、参数类型错误、路径越界或未来权限拒绝。失败本身也是环境反馈。如果 AgentLoop 直接抛异常结束，LLM 看不到错误原因，也无法重新读取文件、修正参数、请求用户确认或解释失败。把失败通过 `ToolResult` 转成 tool message 写回 history，可以保留完整轨迹，让 LLM 基于错误继续决策。当前 `edit_file` 是本地文件工具，通常不涉及网络问题；网络失败更常见于未来真实 LLM adapter 或远程工具。

### 面试题 4：`_tool_result_to_message(...)` 这个小方法为什么是一个有价值的边界？

- 用户回答：不太清楚，我感觉就是可以对特定字段进行选择，然后生成不同情况下的描述。
- 标准回答：这是本轮最需要补强的一题。`ToolResult` 是程序内部结构化对象，`Message.content` 是写给 LLM 的文本观察，二者不是同一层。`_tool_result_to_message(...)` 把“内部结果信封”到“LLM 可读 tool message”的转换集中起来。现在它只是 `str(tool_result)`，但边界固定后，未来可以在这里改成 JSON、增加 trace id、截断大输出、隐藏敏感字段、加入权限审批结果，或适配不同模型厂商的 tool message 格式，而不用在 AgentLoop 主循环里到处改字符串拼接。

### 面试题 5：Day 5 完成后，工具系统距离权限系统还差哪些能力？

- 用户回答：日志、沙箱、人工介入、危险命令的分类和 permission。
- 标准回答：正确。Day 5 后工具系统已经有 schema、`edit_file`、结构化结果和 message history 回写，但还没有权限系统需要的执行前控制。进入 Permission System 前还需要补：危险命令和危险文件操作分类、人工审批流程、权限策略、审计日志、trace id、sandbox 或隔离 runtime、checkpoint / rollback、输出截断、敏感信息脱敏，以及把审批结果纳入 `ToolResult` 或工具轨迹。也就是说，Day 5 解决的是“工具调用能稳定表达和回写”，Permission System 解决的是“工具调用是否允许执行”。

## 第 14 天：2026-06-14

### 面试题 1：为什么 Day 6 要更新 README 和面试讲解稿，而不是继续写新工具？

- 用户回答：Day 6 的主要作用就是对这个星期的任务进行总结。
- 标准回答：方向正确。Day 6 是第 2 周 Tool System 的表达收口日，核心不是新增工具，而是把 Day 1 到 Day 5 的能力整理成外部读者和面试官能理解的 README、架构图和讲解稿。更工程化地说，文档复核也是一种边界校验：确认 README 没有宣称未实现能力，确认 schema、`edit_file`、`ToolResult` 和 AgentLoop 消费边界能串成一条真实链路，并明确当前还不是权限系统、RAG、MCP 或真实 LLM adapter。

### 面试题 2：第 2 周工具系统总链路的每一层分别解决什么问题？

- 用户回答：`Tool` 对工具进行封装 -> `ToolRegistry` 工具的注册路由和统一处理 -> `AgentLoop` 工具与 LLM 的结合。
- 标准回答：抓住了主干。更完整的第 2 周链路是：`ToolParameter / Tool.to_schema()` 解决调用前契约，让模型和程序知道工具参数形状；`ToolRegistry.list_tool_schemas()` 统一导出当前真实注册工具，避免 adapter 手写工具列表；LLM 返回 `ToolCall` 表示调用意图；`AgentLoop` 接收 tool call 并把工具结果写回 message history；`ToolRegistry.run(...)` 负责查找工具、执行工具并把结果包装成 `ToolResult`；`Tool.run(...)` 做基础参数校验；具体工具或 runtime 负责真实读写、编辑、命令执行和安全边界；最后 `_tool_result_to_message(...)` 把内部结构化结果转换成 LLM 可继续消费的 tool message。

### 面试题 3：面试时如何区分“schema 契约”和“具体工具安全校验”？

- 用户回答：schema 契约是编码工具和 LLM 之间的规范，具体的工具校验是真实工具对 LLM 传入参数的兜底。
- 标准回答：正确。schema 契约面向调用前，告诉模型工具叫什么、做什么、需要哪些参数、参数类型和必填字段，也让 `Tool.run(...)` 能做第一层通用校验。具体工具安全校验面向真实执行，处理 schema 无法表达或不应该替代的业务边界，例如路径是否在 `workspace_root` 内、`old_text` 是否唯一、命令是否有超时、工作目录是否存在、未来是否需要人工审批。schema 能减少坏调用，但不能替代 runtime 安全和权限系统。

### 面试题 4：为什么 `ToolResult` 和 `tool Message` 不是同一个层次？

- 用户回答：`ToolResult` 是给程序看的，`Tool Message` 是给 LLM 的。
- 标准回答：正确。`ToolResult` 是程序内部的结构化结果信封，包含 `ok`、`result`、`error_type`、`error_message` 和 `duration_ms`，适合测试、日志、错误分类和后续权限/可观测性扩展。`tool Message` 是写回 message history 给 LLM 继续阅读的观察文本或未来 JSON。二者之间需要一个序列化边界，也就是 `AgentLoop._tool_result_to_message(...)`：当前可以简单转成字符串，未来可以在这里做 JSON 格式、trace id、输出截断、敏感字段隐藏或不同模型厂商的 tool message 适配。

### 面试题 5：第 2 周结束后，进入权限系统前最值得修补的边界缺口是什么？

- 用户回答：`env` 环境和危险命令分类。
- 标准回答：方向正确，尤其危险命令分类是第 3 周 Permission System 的核心入口。更完整地说，进入权限系统前最值得修补的是“工具执行前控制”和“执行轨迹可审计”：危险命令和危险文件操作分类、环境变量和敏感信息处理、人工审批流程、权限策略、审计日志、trace id、sandbox 或隔离 runtime、checkpoint / rollback、输出截断和错误分类枚举。当前 `run_command` 已有 `workspace_root`、`timeout_seconds` 和 `env` 基础边界，但还没有判断命令是否危险，也没有审批和回滚能力。

## 第 15 天：2026-06-14

### 面试题 1：为什么 `run_command` 的 `env` 参数既是能力入口，也是安全风险入口？

- 用户回答：env 会包含敏感信息。
- 标准回答：方向正确。`env` 是能力入口，因为它允许 Agent 给子进程传入必要配置，例如测试变量、PATH、语言环境或未来 API 相关配置；没有它，很多命令无法在隔离环境中正确运行。它也是安全风险入口，因为环境变量常用来保存 `API_KEY`、token、secret、password 等敏感信息。子进程可以读取这些变量，也可能把它们打印到 stdout/stderr；一旦输出进入 `ToolResult`、message history、日志或未来 LLM 上下文，敏感值就会从运行时环境扩散到 Agent 轨迹中。

### 面试题 2：为什么敏感值输出脱敏应该放在 `ShellRuntime` 层，而不是只写在 `ShellCommandTool` 描述里？

- 用户回答：不知道。
- 标准回答：`ShellCommandTool` 的描述只是给模型看的工具契约文本，只能提醒模型“敏感值会脱敏”，不能真正修改命令输出。真正拿到 stdout、stderr、returncode 和 timed_out 的地方是 `ShellRuntime.run(...)`，它直接调用 `subprocess.run(...)` 并封装返回结果。因此输出脱敏应该放在 runtime 层：这里能在结果进入 `ToolResult` 和 message history 之前统一清洗 stdout/stderr。tool 包装层负责暴露工具名、描述和 schema；runtime 层负责真实执行和执行结果边界。

### 面试题 3：输出脱敏和权限审批有什么区别？为什么本次不能把它当成完整 Permission System？

- 用户回答：不知道。
- 标准回答：输出脱敏是执行后的结果清洗：命令已经运行了，只是在 stdout/stderr 返回给 Agent 之前把已知敏感值替换成 `[REDACTED]`。权限审批是执行前控制：在命令真正运行之前判断它是否危险、是否需要用户批准、是否应该拒绝或要求更严格 sandbox。本次 Day 7 只解决“敏感值不要直接进入工具结果和轨迹”的小边界，不会阻止危险命令执行，也没有风险分类、人工审批、策略引擎、审计日志、checkpoint/rollback 或 sandbox，所以不能称为完整 Permission System。

### 面试题 4：当前基于 key 名称识别 `API_KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL` 有什么局限？

- 用户回答：不知道。
- 标准回答：基于 key 名称识别简单直接，但覆盖不完整。第一，敏感变量可能使用其他命名，例如 `PRIVATE_KEY`、`AUTH_HEADER`、`SESSION_COOKIE` 或业务自定义名称；第二，有些变量名看起来不敏感但值本身是 secret；第三，命令可能把 secret 做截断、拼接、编码、base64、hash 或分多段输出，简单字符串替换抓不到；第四，本次只处理显式传入 `env` 的值，不扫描父进程已有环境变量、命令参数、文件内容或第三方程序日志。因此它是最小防线，不是完整 secret scanner。

### 面试题 5：第 2 周完成后，进入第 3 周 Permission System 前，工具系统已经具备了哪些基础？还缺哪些执行前控制能力？

- 用户回答：不知道。
- 标准回答：第 2 周完成后，工具系统已经具备了几个基础：`ToolParameter` 和 `Tool.to_schema()` 能表达工具调用契约；`ToolRegistry.list_tool_schemas()` 能统一导出真实注册工具；`read_file`、`write_file`、`edit_file` 和 `run_command` 有默认工具注册表；`edit_file` 有局部编辑和唯一匹配边界；`ToolRegistry.run(...)` 会返回结构化 `ToolResult`；`AgentLoop._tool_result_to_message(...)` 有结果写回边界；Day 7 还补了 `run_command.env` 敏感输出脱敏。仍然缺少的是执行前控制：危险命令分类、危险文件操作分类、权限策略、人工审批流程、拒绝/允许/询问决策、审计日志、trace id、sandbox、checkpoint/rollback，以及把审批结果纳入工具轨迹。

## 第 16 天：2026-06-18

### 面试题 1：为什么工业级项目里“目录或文件已经存在”不等于“该模块已经实现”？请结合 `src/pca/observability/` 或 `src/pca/context/` 举例说明。

- 用户回答：比如完成一个模块需要三个工具：一个用于创建文件或目录，一个用于整体修改文件，还有一个用于局部匹配修改。创建文件之后，还需要完成文件内容写入；测试后如果出现错误，还要定位问题并修改，才能完成模块的完整开发。所以不是文件或目录存在就代表模块已经实现，还要经过评测和修改。
- 标准回答：目录或文件存在只能说明项目结构已经预留了位置，不代表模块已经接入主链、具备行为、测试覆盖和验收证据。以 `src/pca/observability/` 或 `src/pca/context/` 为例，当前这些目录里的文件主要是占位说明，并没有被 `AgentLoop`、`ToolRegistry` 或工具 runtime 调用，也没有对应单元测试和真实运行链路。因此它们不能算已实现模块。工业级判断应同时看源码行为、调用链接入、测试、示例、文档一致性和失败边界，而不是只看文件是否存在。

### 面试题 2：请沿着当前工具调用主链说明一次 `run_command` 调用会经过哪些核心文件和函数，最终结果如何回写到 `message history`。

- 用户回答：`agent loop -> tool registry .run() -> shell command tool handler -> shell runtime .run() -> stdout stderr time_out returncode -> tool result -> agent loop ._tool_result_to_message() -> message history`。
- 标准回答：一次 `run_command` 调用先由 LLM 产生 `ToolCall(name="run_command", arguments={...})`。`AgentLoop.run(...)` 读取这个 tool call，把 `name` 和 `arguments` 交给 `ToolRegistry.run(...)`；registry 找到 `ShellCommandTool`，再通过 `Tool.run(...)` 做基础参数校验；`ShellCommandTool` 的 handler 转发到 `ShellRuntime.run(...)`。`ShellRuntime` 负责规范化 `command`、解析 `workspace_root` 和 `cwd`、处理 timeout 与 env、调用 `subprocess.run(...)`，然后返回包含 `stdout`、`stderr`、`returncode`、`timed_out`、`duration_ms` 的 dict。`ToolRegistry.run(...)` 把该 dict 包装为 `ToolResult`，`AgentLoop._tool_result_to_message(...)` 再把内部结构化结果转成 `role="tool"` 的 `Message`，追加到 `message history`，让下一轮 LLM 基于真实执行结果继续决策。

### 面试题 3：Week 3 要加入 trace、stats、输出截断和文件资源边界。你会把这些能力分别放在哪些层？为什么不应该把可观测性简单写成散落的 `print`？

- 用户回答：放在可观测层，不好维护。
- 标准回答：方向上对，但需要分层更清楚。`trace_id` 和 `AgentEvent` 这类跨调用链字段应放在 core/events 或 observability 边界，负责贯穿一次 Agent 运行；`ToolRegistry` 适合记录工具调用次数、成功/失败、耗时等 stats，因为它是所有工具执行的统一入口；shell 输出截断应放在 `ShellRuntime` 或工具结果包装边界，保证大输出在进入 `ToolResult` 和 message history 前被控制；文件大小限制和二进制检测应放在 `file_tools.py` 的读写入口，因为那里最接近真实文件系统副作用。不能把可观测性写成散落的 `print`，因为 `print` 没有稳定字段、没有 trace id、无法按工具或一次运行聚合、难以测试，也不方便未来接入审计日志、回放、CI 验证或真实监控系统。

## 第 17 天：2026-06-19

### 面试题 1：trace 和普通 log 的区别是什么？为什么 trace 更适合串起一次 Agent 运行？

- 用户回答：trace 是详细记录 agent 的调用链和其中的细节，普通 log 只是记录某个事件的情况，不能连续。因为 trace 可以根据 trace_id 记录连续的事件，所以可以串起来一次 agent。
- 标准回答：trace 关注一次请求或一次 Agent 运行的完整链路，核心是让多个步骤共享同一个 `trace_id`，从而把用户输入、LLM 响应、工具调用、工具结果和最终回答串成可回放轨迹。普通 log 更偏向记录某个时间点发生的单个事件，除非额外设计关联字段，否则很难稳定还原一次完整调用链。对 Coding Agent 来说，trace 更适合定位是哪一轮、哪一个 tool call、哪一次结果写回导致了后续行为。

### 面试题 2：请说明 `TraceContext.new()` 和 `AgentEvent` 当前分别定义在哪个文件，它们为什么还没有接入 `AgentLoop` 主链？

- 用户回答：`TraceContext.new()` 和 `AgentEvent` 现在都定义在 `src/pca/core/events.py`，不是分别在 `AgentLoop` 和 `Registry`。它们还没接入主链的原因是：Day 2 只做最小数据结构，先证明 API 稳定。
- 标准回答：`TraceContext.new()` 和 `AgentEvent` 都定义在 `src/pca/core/events.py`。Day 2 只验证最小事件模型能生成和保存 `trace_id`、`event_type`、`payload`，暂不接入 `AgentLoop`、`ToolRegistry` 或 `ToolResult`，是为了把数据结构稳定性和主链行为改动分开。接入主链会影响一次 Agent 运行如何创建 trace、如何传递 trace、如何把工具结果挂到 trace 上，这些属于 Day 3 和 Day 4 的渐进加固范围。

### 面试题 3：如果 Day 3 要把 trace 字段接入 `ToolResult`，你会选择哪些字段？如何保证旧测试和旧 message history 不被破坏？

- 用户回答：选择 `trace_id`、`result`、`output_truncated`、`duration_ms`，保留已有的 `duration_ms/result/error_*`。兼容旧测试的方法是给新字段默认值，并保持 `ToolResult.__str__()` 输出不变，旧的 message history 就不会被破坏。
- 标准回答：Day 3 最适合在 `ToolResult` 中新增 `trace_id`、`tool_call_id` 和 `output_truncated`，并继续保留已有的 `ok`、`result`、`error_type`、`error_message`、`duration_ms`。`trace_id` 负责关联一次 Agent 运行，`tool_call_id` 负责区分同一个 trace 下的具体工具调用，`output_truncated` 负责告诉调用方输出是否被截断。兼容旧测试和旧 message history 的关键是给新增字段默认值，例如 `None` 或 `False`，并保持 `ToolResult.__str__()` 的成功和失败文本语义不变；这样旧的 `AgentLoop._tool_result_to_message(...)` 仍能得到同样的 `Message.content`。

## 第 18 天：2026-06-19

### 面试题 1：为什么 `trace_id` 和 `tool_call_id` 不是同一个字段？请结合“一次 Agent 运行”和“一次工具调用”的粒度差异回答。

- 用户回答：`trace_id` 标识的是 Agent 一次调用的标识，`tool_call_id` 标识的是工具调用的标识，同时可能对应着某个工具。
- 标准回答：方向正确。`trace_id` 是一次 Agent 运行或一次用户任务的链路标识，应该贯穿 `user_input -> LLM -> tool call -> tool result -> recovery/final answer`。同一个 trace 里可能有 0 次、1 次或多次工具调用。`tool_call_id` 是其中某一次具体工具调用的标识，用来区分同一个 trace 下多次调用同一个工具、重试同一个工具、或调用不同工具的结果。二者粒度不同：`trace_id` 解决“这属于哪一次任务”，`tool_call_id` 解决“这是这次任务里的哪一次工具调用”。

### 面试题 2：请说明 `ToolResult.__str__()` 当前在什么兼容边界上起作用。为什么 Day 3 新增 `trace_id`、`tool_call_id`、`output_truncated` 后仍然不能改变 `__str__()` 的输出？

- 用户回答：兼容工具的结构化输出结果和工具输出结果作为 LLM 的上下文的边界；因为这几个字段对于上下文影响 LLM 决策的效果甚小几乎没有，这几个字段是作为追踪、恢复、审查和日志来用的。
- 标准回答：整体正确，但需要把边界说得更精确。`ToolResult.__str__()` 当前是 `ToolResult` 这个内部结构化结果信封到 `AgentLoop._tool_result_to_message(...)` 写回 `message history` 的文本兼容边界。成功时它返回原始结果文本，失败时返回稳定的 `Tool execution failed: ...` 文本。新增 `trace_id`、`tool_call_id`、`output_truncated` 后不能改变 `__str__()`，核心原因是旧测试、旧示例和旧 message history 依赖这个文本语义；如果把元数据直接混进字符串，LLM 上下文会变得不稳定，也会把观测字段和业务观察文本混在一起。元数据应保留在结构化字段中，供 trace、恢复、审计、日志和后续统计使用。

### 面试题 3：如果 Day 5 实现输出截断，你会把“截断后的文本”和 `output_truncated=True` 分别放在哪里？请说明边界情况、方案对比和测试思路。

- 用户回答：截断后的文本和 `output_truncated=True` 放在 `ToolResult` 中。
- 标准回答：方向接近，但还不够分层。截断动作应该发生在最接近大输出产生的位置，例如 `ShellRuntime` 返回 stdout/stderr 前，或 file tool 读取文件内容进入 `ToolResult` 前；这样可以防止大输出先污染内存、`ToolResult` 和 message history。截断后的文本可以作为 `ToolResult.result` 里的内容保存，例如 shell result 的 `stdout` 或 `stderr` 已经是截断后的文本；`output_truncated=True` 应作为 `ToolResult` 的结构化元数据保存，告诉调用方这不是完整输出。只把提示写进字符串的方案不够好，因为难以测试、统计和审计；只放 bool 不改文本也不够，因为 LLM 仍可能看到过大的上下文。测试上应覆盖：未超过上限时文本不变且 `output_truncated=False`；超过上限时文本被截断且 `output_truncated=True`；stdout 和 stderr 至少一个被截断时总标记为 true；截断后 `ToolResult.__str__()` 仍保持兼容，不额外泄露结构化字段。

## 第 19 天：2026-06-20

### 面试题 1：为什么工具调用统计应该放在 `ToolRegistry.run(...)` 这个统一入口，而不是放在每个具体工具的 handler 里？

- 用户回答：因为工具调用统计是统计每种工具的情况，作为总入口和 registry 同级，并且方便管理。
- 标准回答：方向正确。更完整地说，stats 统计的是“工具系统运行情况”，不是某个具体工具的业务逻辑。`ToolRegistry.run(...)` 是 `AgentLoop` 面向工具系统的统一入口，所有工具成功、handler 抛错、参数校验失败、未知工具调用都会经过这里或在这里被捕获，因此放在 registry 能保证统计口径统一。如果把统计散落到每个 handler 里，容易漏掉参数校验失败和未知工具，也会让文件工具、shell 工具、未来 MCP 工具都混入重复的观测逻辑。具体工具应该专注真实业务边界，例如读文件、写文件、执行命令；registry 负责路由、结果包装和聚合统计。

### 面试题 2：请沿着当前源码说明一次成功工具调用如何从 `ToolRegistry.run("echo", {"text": "hello"})` 走到 `_record_stats(...)`，并说明失败路径在哪里更新 `failures`。

- 用户回答：不清楚；在 tools.run() 返回结果来判断是否失败。
- 标准回答：一次成功调用从 `ToolRegistry.run(name, arguments)` 开始。首先记录 `started_at = perf_counter()`；然后检查 `arguments` 必须是 dict；接着通过 `self.get(name)` 找到注册工具；再调用 `tool.run(arguments)`，由 `Tool.run(...)` 做参数校验并进入 handler。如果 handler 成功返回，例如 `"hello"`，registry 计算 `duration_ms`，调用 `self._record_stats(name=name, ok=True, duration_ms=duration_ms)`，这里会把 `calls += 1`、`successes += 1`、`total_duration_ms += duration_ms`，最后返回 `ToolResult.success(...)`。失败路径在 `except Exception as exc:` 中处理：无论是未知工具、参数错误还是 handler 抛错，都会构造 `ToolResult.from_exception(...)`，然后调用 `_record_stats(name=name, ok=False, duration_ms=duration_ms)`，这里会把 `calls += 1`、`failures += 1`。所以不是等外部调用方拿到 `ToolResult` 再判断，而是在 `ToolRegistry.run(...)` 内部根据 try/except 的成功或失败分支同步更新 stats。

### 面试题 3：如果未来要把 stats 暴露给 CLI 或 Web UI，你会如何设计 `get_stats()` 的返回格式、重置策略和权限边界？请同时回答未知工具统计、stats/trace/log 存储边界、并发安全和防外部篡改测试。

- 用户回答：不清楚。
- 标准回答：可以先保持 `get_stats()` 返回只读快照，例如 `{tool_name: {"calls": int, "successes": int, "failures": int, "total_duration_ms": int}}`，CLI 可以直接表格展示，Web UI 可以再加成功率和平均耗时等派生字段。重置策略不要混进 `get_stats()`，可以单独提供 `reset_stats()` 或按 session 新建 registry，避免“读取统计”产生副作用。权限边界上，stats 不应包含原始参数、文件内容、stdout、stderr 或 secret，只暴露聚合指标；如果未来按项目、用户、session 展示，还需要只允许用户查看自己授权工作区的统计。

  未知工具应该单独统计，而且可以按请求的工具名记录，因为它能暴露 LLM 幻觉、schema 漂移或 adapter 映射错误。stats、trace、log 不应该简单混在一个结构里：stats 是聚合指标，trace 是一次请求的链路，log 是可审计事件记录，它们可以共享 `trace_id` / `tool_name` 等关联字段，但存储和查询方式不同。并发执行时，当前 `_stats` 的普通 dict 自增不是严格线程安全，未来需要锁、单线程事件队列、原子计数器或集中 metrics backend。防外部篡改的测试应覆盖 `stats = registry.get_stats(); stats["echo"]["calls"] = 999; assert registry.get_stats()["echo"]["calls"] == 1`，证明返回的是快照而不是内部可变对象。

## 第 20 天：2026-06-20

### 面试题 1：为什么输出截断不能只靠 LLM 自己“少输出一点”？请分别从工具执行、上下文长度和可测试性角度回答。

- 用户回答：上下文有限制，导致读取的文件长度有限制，并且工具执行的时候需要读取文件内容所以要有长度限制，并且再观测角度，内容太长不利于观测，只需要保留关键信息即可。
- 标准回答：方向正确。LLM 的提示词只能影响模型“想怎么调用工具”，不能约束工具真实返回多少内容；`run_command` 可能输出几百 KB stdout/stderr，`read_file` 也可能读到很长文件，这些都发生在工具执行结果边界，不能靠模型自觉控制。上下文长度上，大输出会挤占 message history，导致后续用户需求、代码片段、错误信息或安全事件被压掉。可测试性上，必须有明确的 `truncate_output(...)` 行为和 `ToolResult.output_truncated` 元数据，才能写单元测试证明“短输出不变、长输出被截断、LLM 知道内容不完整”。只说“保留关键信息”还不够，因为当前 Day 5 是固定前缀截断，不是语义摘要；语义摘要属于后续 context compression 或观察压缩能力。

### 面试题 2：沿着 `ToolRegistry.run("run_command", ...) -> ShellRuntime.run(...) -> _truncate_tool_result_payload(...) -> ToolResult.success(...)` 说明：大 stdout/stderr 是在哪一层被截断的？`output_truncated=True` 是在哪里设置的？

- 用户回答：工具执行层；ToolRegistry。
- 标准回答：关键点要更精确：`ShellRuntime.run(...)` 负责真实命令执行、cwd/timeout/env 处理和 stdout/stderr 捕获，它仍返回 raw dict。截断发生在 `ToolRegistry.run(...)` 的成功路径里，也就是 registry 拿到具体工具返回值之后、调用 `ToolResult.success(...)` 之前。具体函数是 `_truncate_tool_result_payload(...)`：它识别 dict 里的 `stdout`、`stderr` 字段并调用 `truncate_output(...)` 分别截断；如果任一字段发生截断，就返回 `output_truncated=True`。随后 `ToolRegistry.run(...)` 把这个布尔值传给 `ToolResult.success(..., output_truncated=output_truncated)`。所以可以说在工具结果包装边界截断，但不能说是在 `ShellRuntime` 本身截断。

### 面试题 3：如果一个命令同时输出 200KB stdout 和 20KB stderr，你会选择分别截断还是合并后截断？请说明方案取舍，并补充如何让 LLM 知道输出不完整、如何保留排障信息、如何测试未截断/截断路径。

- 用户回答：合并之后截断；根据表示也就是提示词；利用一些概要的模型保留关键信息；看输出。
- 标准回答：这是本次最需要修正的一题。当前实现选择分别截断 stdout 和 stderr，而不是合并后截断。原因是 stdout 和 stderr 语义不同：stdout 通常是正常输出，stderr 通常包含错误、warning、traceback 或诊断信息；如果先合并再截断，200KB stdout 可能把 20KB stderr 中真正重要的错误信息挤掉。分别截断可以保证两个通道都保留各自前缀和截断标记。

  LLM 知道输出不完整有两层机制：第一，截断文本中追加 `[output truncated: kept ...]` 这种可见标记；第二，`ToolResult.output_truncated=True` 作为结构化元数据保留，后续 trace、日志、UI 或观察压缩可以直接读取。排障信息的最小保留方式是 stdout/stderr 各自保留前缀、returncode、timed_out、duration_ms 等结构化字段不变；未来可以升级为 head+tail、按错误行优先保留、保存完整原始输出到审计文件或生成摘要，但 Day 5 只做最小可测截断。测试上要覆盖：短 stdout/stderr 不变且 `output_truncated=False`；大 stdout 或大 stderr 被截断且 `output_truncated=True`；stdout/stderr 同时超限时两个字段都带截断标记；`read_file` 这类字符串 payload 超限时也被截断；旧 `ToolResult.__str__()` 和示例兼容。

## 第 21 天：2026-06-20

### 面试题 1：为什么文件大小限制不能只靠 Day 5 的输出截断解决？请从读取前资源消耗、LLM 上下文和错误语义三个角度回答。

- 用户回答：不清楚。
- 标准回答：输出截断和文件大小限制解决的是两个不同边界。输出截断发生在工具已经产生结果之后，只能控制写入 `ToolResult` 和 message history 的文本长度；如果 `read_file` 已经把一个超大文件读进内存，再截断就太晚了，读取本身已经消耗了内存、I/O 和时间。LLM 上下文角度，截断能减少最终观察文本，但不能告诉系统“这个资源本来就不适合文本读取”。错误语义角度，大文件应该明确返回“文件太大，拒绝读取”，而不是假装成功并返回一段截断内容；这样 Agent 才能决定换策略，例如请求用户确认、读取片段、用日志工具或跳过该文件。

### 面试题 2：请沿着 `ToolRegistry.run("read_file", ...) -> ReadFileTool._run(...) -> _ensure_readable_text_file(...) -> ToolResult.from_exception(...)` 说明大文件或二进制文件如何被拒绝并回写成结构化失败。

- 用户回答：不清楚。
- 标准回答：一次 `read_file` 调用从 `ToolRegistry.run("read_file", arguments)` 开始。registry 先检查 `arguments` 是字典，再找到注册的 `ReadFileTool`，调用 `Tool.run(...)` 做 `path` 等基础参数校验。随后进入 `ReadFileTool._run(...)`，先通过 `_resolve_workspace_path(...)` 确认路径仍在 `workspace_root` 内，并拒绝目录。真正读取文本前，`_ensure_readable_text_file(path)` 先用 `path.stat().st_size` 检查文件大小；如果超过 1MiB，就抛出 `ValueError("file is too large...")`。如果大小通过，再用二进制模式读取前 1024 字节；如果样本里有 NUL 字节，就抛出 `ValueError("file appears to be binary...")`。这些异常会被 `ToolRegistry.run(...)` 的 `except` 捕获，并通过 `ToolResult.from_exception(...)` 转成 `ok=False`、`error_type="ValueError"`、`error_message=...` 的结构化失败结果，后续 `AgentLoop._tool_result_to_message(...)` 可以把失败观察写回 message history。

### 面试题 3：如果未来要支持读取超大日志或图片文件，你会如何设计“直接拒绝、分块读取、摘要读取、专门二进制工具”这几种方案？请说明边界情况、方案对比和测试思路。

- 用户回答：不清楚。
- 标准回答：最保守的默认方案是直接拒绝：普通 `read_file` 只处理小型文本文件，遇到超大文件或明显二进制文件直接失败，优点是安全、简单、可测试，缺点是不能处理大日志和图片。对超大日志，可以新增分块读取或 head/tail 读取工具，例如 `read_file_chunk(path, offset, max_bytes)` 或 `read_file_tail(path, lines)`，让 Agent 有边界地查看部分内容；测试要覆盖 offset 越界、块大小上限、UTF-8 边界和不会突破 `workspace_root`。摘要读取适合日志、测试报告、长 markdown 等文本资源，可以先读取受限片段或流式扫描后生成结构化摘要；测试要覆盖摘要不会吞掉关键错误行，并保留“摘要不是全文”的元数据。图片、压缩包、PDF 等二进制资源不应该塞进文本 `read_file`，应有专门二进制工具，例如读取元数据、提取文本、生成预览或交给视觉/文档解析模块；测试要覆盖 MIME/魔数识别、大小限制、不可解析文件失败和敏感路径边界。总体原则是：默认文本读取要窄，特殊资源通过专门工具扩展，而不是让 `read_file` 变成万能入口。

## 第 22 天：2026-06-20

### 面试题 1：Day 7 为什么只新增 `examples/03_observed_tool_run.py` 和验收测试，而不继续新增 Permission System？

- 用户回答：Day 7 不继续做 Permission System，是因为 Day 7 是 Week 3 的加固验收日，目标是确认 Tool Runtime 已经完成的 trace 数据结构、ToolResult 元数据、stats、输出截断、文件资源限制和示例验证是否真实可用。Permission System 是 Week 4 的新模块，如果提前做，会把新模块和本周验收混在一起，导致边界不清。
- 标准回答：正确。Day 7 的职责是验收 Week 3 的 Agent Core + Tool Runtime 加固结果，不是开启新模块。`examples/03_observed_tool_run.py` 的作用是用一个可运行示例证明当前真实能力：成功读取、资源拒绝、结构化 `ToolResult` 和 `ToolRegistry.get_stats()`。Permission System 属于 Week 4 的执行前控制，如果在 Day 7 提前接入，会把“本周加固验收”和“下周新能力实现”混在一起，导致文档、测试和架构边界不清，也容易把尚未实现的权限审批误说成已完成能力。

### 面试题 2：从 `examples/03_observed_tool_run.py` 开始，说明成功读取和二进制拒绝分别经过哪些函数，最后如何进入 `ToolResult` 和 `ToolRegistry.get_stats()`。

- 用户回答：调用链是：`examples/03_observed_tool_run.py -> create_coding_tool_registry() -> ToolRegistry.run("read_file", ...) -> ToolRegistry.get("read_file") -> Tool.run(arguments) -> ToolParameter.validate(arguments) -> ReadFileTool._run(arguments) -> _resolve_workspace_path(arguments) -> _ensure_readable_text_file(path)`。成功读取时，`_ensure_readable_text_file(path)` 通过检查，然后 `path.read_text(...)` 返回文本，`ToolRegistry.run(...)` 把结果包装成 `ToolResult.success(...)`，并记录 stats 成功次数。二进制拒绝时，`_ensure_readable_text_file(path)` 发现文件采样中有 NUL 字节，抛出 `ValueError`。`ToolRegistry.run(...)` 捕获异常，把它转换成 `ToolResult.from_exception(...)`，并记录 stats 失败次数。最后 `registry.get_stats()` 返回 `read_file` 的 `calls=2`、`successes=1`、`failures=1`。
- 标准回答：正确。补充一点：成功路径中 `ToolRegistry.run(...)` 会在工具返回文本后调用 `_truncate_tool_result_payload(...)`，当前短文本不会触发截断，因此 `output_truncated=False`，随后返回 `ToolResult.success(...)` 并调用 `_record_stats(name="read_file", ok=True, ...)`。失败路径中，二进制检测发生在真正 `read_text(...)` 之前，异常被 registry 的 `except` 捕获，转换成 `ok=False`、`error_type="ValueError"`、`error_message=...` 的结构化失败，并通过 `_record_stats(..., ok=False, ...)` 记录一次失败。`get_stats()` 返回的是统计快照，不暴露内部 `_stats` 可变对象。

### 面试题 3：如果要把当前 stats 升级成工业级 observability，你会如何设计 logger hook、trace_id 透传、持久化 metrics 和查询接口？请说明边界情况、方案对比和测试方法。

- 用户回答：在一次 Agent run 开始时创建 `trace_id`，并传给 `AgentLoop -> ToolRegistry.run(...) -> ToolResult`，这样一次任务里的 LLM 调用、工具调用、工具结果能串起来。在 `ToolRegistry.run(...)` 前后加 logger hook，记录结构化 JSON 日志，包括 `trace_id`、`tool_name`、参数摘要、成功/失败、错误类型、耗时、是否截断。stats 不只放在内存里，而是持久化到文件、SQLite 或 metrics backend，避免进程退出后数据丢失。提供查询接口，比如按 `trace_id` 查完整链路，按 `tool_name` 查调用次数、成功率、失败率、平均耗时、P99。边界情况包括：工具抛异常、参数校验失败、未知工具、输出被截断、敏感参数脱敏、并发调用 stats 是否线程安全。测试方法包括：单测 logger 字段，集成测试 `trace_id` 是否全链路一致，安全测试日志不泄漏 token，压力测试并发 stats 不丢数据。
- 标准回答：正确。工业级 observability 不能只靠当前内存 stats。更完整的设计是：`AgentLoop.run(...)` 创建或接收 `TraceContext`，把 `trace_id` 传入每次工具调用；`ToolRegistry.run(...)` 在调用前后触发 logger hook，记录结构化事件；`ToolResult` 保存 `trace_id`、`tool_call_id`、`output_truncated` 等元数据；metrics 层把聚合指标写入可持久化后端；查询层支持按 trace、tool、session 或时间窗口检索。方案取舍上，内存 stats 简单但不可恢复，JSONL 易审计但查询弱，SQLite 查询方便但要设计 schema，OpenTelemetry 更标准但接入成本更高。测试必须覆盖成功、失败、未知工具、参数错误、截断、脱敏、并发和进程重启后的可查询性。

## 第 23 天：2026-06-21

### 面试题 1：风险分类和权限拦截有什么区别？为什么 `classify_command(...)` 不应该直接执行或阻止命令？

- 用户回答：风险分类是根据命令的风险进行评估，来影响后续的执行流程。权限拦截是根据当前 LLM 的决策给出的操作来进行拦截，比如删除系统文件，风险分类给出 deny，但是具体的操作是由权限拦截进行；`classify_command` 只是进行命令的分类，秉持着单一原则。
- 标准回答：方向正确。风险分类回答的是“这条命令看起来属于什么风险等级”，输出是 `RiskAssessment(level, reason, matched_rule)`；权限拦截回答的是“这一次工具调用是否允许继续执行”，输出通常是 allow / ask / deny 这样的策略决策，并可能触发人工审批或直接拒绝。`classify_command(...)` 不应该执行命令，也不应该直接阻止命令，因为它的职责是纯分类：不依赖运行时环境、不产生副作用、容易单元测试、可被后续 `PermissionPolicy.decide(...)`、审批对象、审计日志和 shell gate 复用。真正的拦截应放在执行前 gate 中，由策略结合风险等级、工具类型、用户设置和审批结果做最终决策。

### 面试题 2：请按调用链解释 `classify_command("python -c \"print(1)\"")` 如何得到 `RiskLevel.ASK`，并指出 `reason` 和 `matched_rule` 的作用。

- 用户回答：不知道，请直接给出答案。
- 标准回答：调用从 `classify_command(command)` 开始。输入是字符串 `"python -c \"print(1)\""`，先进入 `_normalize_command(...)`：因为 command 是非空字符串，所以用 `shlex.split(command, posix=False)` 尝试切分成命令片段，例如 `("python", "-c", "\"print(1)\"")`。随后 `classify_command(...)` 构造 `lowered_parts` 和 `lowered_text`，先调用 `_match_deny_rules(...)`；这条命令不是 `rm -rf`、`del /s /q`、`Remove-Item -Recurse/-Force` 或 `format`，所以不会得到 `DENY`。接着进入 `_match_ask_rules(...)`，其中 `_uses_inline_code(lowered_parts)` 会看到可执行文件是 `python`，并且参数中包含 `-c`，于是返回 `RiskAssessment(level=RiskLevel.ASK, reason="Inline code execution can run arbitrary logic.", matched_rule="inline_code")`。`reason` 给人和后续 UI 解释为什么要询问；`matched_rule` 给测试、审计和调试使用，说明具体命中了哪条规则。

### 面试题 3：如果未来要把风险分类接入 `run_command`，你会把 gate 放在 `ShellRuntime`、`ShellCommandTool` 还是 `ToolRegistry`？请比较方案，并说明边界情况、误判处理、审计记录和测试策略。

- 用户回答：`ShellRuntime`，有利于结果的回显和统计。
- 标准回答：这个答案需要修正。`ShellRuntime` 是真实执行命令的底层 runtime，放 gate 的优点是可以作为最后防线，保护所有直接调用 runtime 的路径；但它太低层，不适合做人类审批、工具级策略、LLM tool call 上下文、审计事件和 UI 交互，也不应该承担 `ToolRegistry` 的统计和结果包装职责。`ShellCommandTool` 是 shell 专属 gate 的简单位置，能在调用 runtime 前分类并阻止危险命令，适合 Day 4 最小接入；缺点是只覆盖 shell 工具，未来文件写入、MCP 工具等还要重复实现。`ToolRegistry` 的执行前 hook 更适合作为长期方案，因为所有工具调用都经过 registry，能统一记录 allow / ask / deny、工具名、参数摘要、trace_id、审批结果和 stats；缺点是 registry 需要可插拔 policy，不能把 shell 专属规则硬编码进去。

  更稳的设计是：短期把 shell gate 放在 `ShellCommandTool` 或 `ToolRegistry` 的执行前边界；长期在 `ToolRegistry.run(...)` 增加通用 permission hook，让不同工具提供自己的 risk classifier；`ShellRuntime` 保留少量不可绕过的低层安全校验，例如 workspace、cwd、timeout，必要时作为最后防线。误判处理上，`ASK` 交给用户确认，`DENY` 默认拒绝但允许未来通过显式高级策略覆盖，`SAFE` 也要保留审计记录。审计记录至少包含 tool name、command 摘要、risk level、matched_rule、decision、reason、trace_id、时间和是否执行。测试策略包括：危险命令不会进入 runtime；`ASK` 生成审批请求；审批拒绝时不执行；审批通过时才执行；未知或解析失败命令默认偏保守；审计日志不泄漏敏感环境变量。

## 第 24 天：2026-06-21

### 面试题 1：`RiskLevel` 和 `DecisionAction` 为什么不能合并成一个枚举？请分别说明“风险分类”和“策略判断”回答的问题。

- 用户回答：因为二者的边界不同。
- 标准回答：方向正确，但需要说清楚“边界不同”具体是什么。`RiskLevel` 是风险分类结果，回答“这个命令或工具调用本身看起来多危险”，例如 `SAFE`、`ASK`、`DENY`；它来自 `classify_command(...)`，属于事实判断。`DecisionAction` 是策略判断结果，回答“在当前策略下系统准备怎么处理这次调用”，例如 `ALLOW`、`ASK`、`DENY`；它来自 `PermissionPolicy.decide(...)`，属于策略动作。二者不能合并，因为同一个风险等级在不同配置下可能产生不同动作：例如 `RiskLevel.ASK` 默认需要审批，但在可信 workspace 或用户显式配置下未来可能变成 `ALLOW`；反过来某些低风险命令在只读模式下也可能被策略拒绝。分开后，风险分类、策略配置、审批对象和审计记录才能独立演进。

### 面试题 2：从 `classify_command("curl https://example.com")` 到 `PermissionPolicy().decide(...)`，请按当前源码说明数据如何从 `RiskAssessment` 变成 `PermissionDecision`，并指出今天为什么没有接入 `ShellRuntime`。

- 用户回答：不清楚，请直接给出答案。
- 标准回答：调用从 `classify_command("curl https://example.com")` 开始。`classify_command(...)` 先用 `_normalize_command(...)` 把字符串命令切成片段，得到类似 `("curl", "https://example.com")`。然后它构造 `lowered_parts` 和 `lowered_text`，先走 `_match_deny_rules(...)`；这条命令不是递归删除、Windows 删除、PowerShell `Remove-Item` 或 `format`，所以不会被判为 `DENY`。接着进入 `_match_ask_rules(...)`，因为第一个命令片段是 `curl`，命中 `network_access` 规则，于是返回 `RiskAssessment(level=RiskLevel.ASK, reason="Network commands can read from or write to external systems.", matched_rule="network_access")`。

  这个 `RiskAssessment` 再传给 `PermissionPolicy().decide(assessment)`。`decide(...)` 先检查输入必须是 `RiskAssessment`，然后根据 `assessment.level` 做映射：`SAFE -> DecisionAction.ALLOW`、`ASK -> DecisionAction.ASK`、`DENY -> DecisionAction.DENY`。所以 `curl` 的结果会变成 `PermissionDecision(action=DecisionAction.ASK, reason="Ask risk assessments require approval before execution.", assessment=assessment)`，并保留原始 `assessment` 作为后续审批和审计的证据。

  今天没有接入 `ShellRuntime`，是因为 Day 2 只稳定策略判断 API。`ShellRuntime` 是真实执行命令的层，一旦接入就会影响 `run_command` 的主链行为。现在还没有审批对象、审批结果和审计事件，如果过早接入 runtime，就会把“分类”“策略”“审批”“执行拦截”混在一起，测试和文档边界都会变模糊。真正的 shell gate 留到 Week 4 Day 4。

### 面试题 3：如果未来项目支持用户配置“允许 curl 访问公司内网，但外网仍需审批”，你会如何扩展 `PermissionPolicy`？请说明需要新增哪些输入信息、默认策略如何避免误放行、审批对象和审计事件应分别记录什么，以及如何测试 `DENY` 命令的硬拒绝边界。

- 用户回答：不清楚，请直接给出答案。
- 标准回答：可以把 `PermissionPolicy.decide(...)` 从只接收 `RiskAssessment` 扩展为接收一个更完整的上下文，例如 `PermissionContext(tool_name, command, assessment, workspace_root, user_config, trace_id)`。用户配置里可以有允许访问的域名或网段，例如 `allowed_network_hosts=["intranet.example.com"]`，并且必须明确区分内网 host 和任意外网 URL。策略逻辑应先保留硬边界：如果 `assessment.level is RiskLevel.DENY`，默认直接返回 `DecisionAction.DENY`，不被普通 allowlist 覆盖；只有经过非常明确的高级策略和强审计才可能例外。然后再处理 `ASK`：如果命令是 `curl`，目标 host 在允许列表里，可以返回 `ALLOW`；否则仍返回 `ASK`。

  默认策略要避免误放行：配置缺失、URL 解析失败、host 不在 allowlist、命令不是明确支持的网络命令、或匹配规则不确定时，都应该偏保守返回 `ASK` 或 `DENY`，不能默认 `ALLOW`。审批对象 `ApprovalRequest` 应记录给用户看的上下文：工具名、命令摘要、风险等级、策略原因、待批准动作、过期时间和 trace id。审计事件应记录系统可追溯证据：请求时间、决策动作、风险等级、matched_rule、policy_rule、用户是否批准、是否实际执行、trace id、工具名和脱敏后的命令摘要。

  测试上至少要覆盖四类：第一，`curl https://intranet.example.com` 在配置允许时得到 `ALLOW`；第二，`curl https://example.com` 不在 allowlist 时仍是 `ASK`；第三，URL 解析失败或配置缺失时不会误放行；第四，`rm -rf /` 这类 `RiskLevel.DENY` 即使配置里写了 allow，也必须返回 `DENY`，并确认不会进入后续 runtime。这样才能证明“内网例外”没有破坏高危命令的硬拒绝边界。

## 第 25 天：2026-06-22

### 面试题 1：`PermissionDecision(action=ASK)` 和 `ApprovalRequest` 的区别是什么？为什么不能把 `ASK` 直接当成“用户已经同意执行”？

- 用户回答：`PermissionDecision(action=ASK)` 是系统策略层的判断，意思是这次工具调用不能直接执行，需要询问用户。`ApprovalRequest` 是真正交给用户审批的请求对象，保存请求 id、工具名、命令摘要、策略判断、创建时间和过期时间。不能把 `ASK` 当成用户已经同意执行，因为 `ASK` 只是系统说“需要问”，不是用户说“同意”；真正代表用户同意的是 `ApprovalDecision(approved=True)`。
- 标准回答：正确。`PermissionDecision(action=ASK)` 属于 policy 层，表达系统策略动作：这次调用需要人工确认。`ApprovalRequest` 属于审批层，表达一次可审查、可展示、可关联的请求，包含 `request_id`、`tool_name`、`command_summary`、原始 `PermissionDecision`、`created_at` 和 `expires_at`。二者不能混淆：`ASK` 是“需要问”，不是“已经批准”；只有用户返回 `ApprovalDecision(approved=True)`，且请求未过期、request id 匹配时，后续 shell gate 才能考虑执行。

### 面试题 2：请沿着 `classify_command(...) -> PermissionPolicy.decide(...) -> ApprovalRequest -> ApprovalDecision` 说明：每一层分别保存了哪些信息，哪一层开始出现用户理由？

- 用户回答：`classify_command(...)` 输出 `RiskAssessment`，保存 `level`、`reason`、`matched_rule`。`PermissionPolicy.decide(...)` 输出 `PermissionDecision`，保存 `action`、`reason`、`assessment`。`ApprovalRequest` 保存一次待审批请求，包括 `request_id`、`tool_name`、`command_summary`、`decision`、`created_at`、`expires_at`。`ApprovalDecision` 保存用户最终决定，包括 `request_id`、`approved`、`user_reason`、`decided_at`。用户理由从 `ApprovalDecision.user_reason` 开始出现，因为只有用户做出批准或拒绝时，才有用户为什么这么决定。
- 标准回答：正确。调用链的职责边界是：`classify_command(...)` 做风险事实判断，`PermissionPolicy.decide(...)` 做系统策略判断，`ApprovalRequest` 把一次需要人工确认的策略判断包装成请求，`ApprovalDecision` 才记录用户的批准或拒绝。`user_reason` 不应该提前出现在 `RiskAssessment` 或 `PermissionDecision` 中，因为前两者是系统判断；用户理由只属于用户实际做出决定的那一刻。

### 面试题 3：如果一个审批请求已经过期，后续 shell gate 应该如何处理？请说明边界情况、优化思路、方案对比，以及你会如何测试这个行为。

- 用户回答：如果审批请求已经过期，shell gate 应该拒绝执行，并要求重新生成审批请求。过期请求可能已经脱离当前上下文，比如代码、目录、任务状态都变了，继续执行会有安全风险。边界情况包括：`now == expires_at` 视为已过期；用户批准了一个已过期请求也不能执行；`request_id` 不匹配不能执行；用户拒绝不能执行；只有用户批准且未过期才允许进入 shell 执行。方案上，保守方案是过期直接拒绝并重新审批，安全性最好，当前项目应采用；宽松方案是给宽限时间，但安全边界变模糊；自动刷新方案是重新生成请求并再次询问用户，适合后续 UI/CLI 完善后实现。测试上应覆盖已过期拒绝、刚好等于 `expires_at` 拒绝、未过期且批准允许、未过期但拒绝时拒绝执行。
- 标准回答：正确。Day 4 的 shell gate 应采用保守语义：审批请求过期时直接拒绝执行，不把旧审批继续用于当前命令。关键边界是 `now >= expires_at` 都算过期；即使 `ApprovalDecision.approved=True`，只要请求过期、request id 不匹配或审批结果为拒绝，都不能进入 runtime。长期可以引入重新生成请求、CLI 重新提示或 UI 自动刷新，但默认不能给静默宽限。测试必须证明危险命令在过期、拒绝、id 不匹配时不会调用真实 runtime，只有未过期且批准的请求才会继续执行。

## 第 26 天：2026-06-22

### 面试题 1：shell gate 为什么放在 `ShellCommandTool`，而不是放在 `ShellRuntime` 或 `ToolRegistry`？

- 用户回答：因为 `ShellCommandTool` 是 `run_command` 这个工具的执行前边界，最适合做“这次 shell 工具调用能不能执行”的判断。不放在 `ShellRuntime`，是因为 `ShellRuntime` 应该保持底层执行器职责，只负责 workspace、cwd、timeout、env、stdout/stderr 等运行时安全边界，不应该混入业务权限策略。不放在 `ToolRegistry`，是因为 `ToolRegistry` 是通用工具路由层，负责注册、查找、统计、包装 `ToolResult`，不应该理解 shell 命令风险。否则以后文件工具、MCP 工具、git 工具的风险逻辑都会污染 registry。
- 标准回答：正确。`ShellCommandTool` 是当前 `run_command` 的工具语义边界，能在调用 `ShellRuntime.run(...)` 前做风险分类和策略判断。`ShellRuntime` 更适合保持为底层执行器，继续负责 workspace、cwd、timeout、env、输出捕获和敏感输出脱敏；如果把权限策略塞进去，会让 runtime 同时承担业务权限和执行细节。`ToolRegistry` 是通用路由、统计、截断和 `ToolResult` 包装层；如果直接硬编码 shell 风险规则，会污染所有工具。长期可以在 registry 增加可插拔 permission hook，但每个工具的风险分类仍应由对应工具或 classifier 提供。

### 面试题 2：如何用测试证明 `DENY` 和 `ASK` 没有进入真实 runtime？为什么只看返回值不够？

- 用户回答：用一个 fake runtime / recording runtime，它的 `run(...)` 会记录自己是否被调用。构造 `ShellCommandTool(runtime=fake_runtime)`，执行 `rm -rf .` 这类 `DENY` 命令，断言返回失败 `ToolResult`，更关键的是断言 `fake_runtime.calls == []`。`ASK` 也是一样，比如 `curl https://example.com`，应该返回需要审批的失败结果，并且 `fake_runtime.calls == []`。只看返回值不够，因为返回失败可能是命令已经执行后失败，也可能是 runtime 内部报错。要证明的是“执行前拦截”，所以必须观察 runtime 是否完全没被调用。
- 标准回答：正确。Day 4 的测试重点不是“最终失败”，而是“执行前没有进入真实执行层”。fake runtime 的价值是把副作用边界变成可观察状态：只要 `calls` 为空，就能证明 gate 在 runtime 前阻断了命令。返回值只能证明调用结果是失败，不能区分失败发生在 permission gate、runtime 参数校验、subprocess 执行失败还是命令自身失败。工业级安全测试必须验证副作用没有发生，所以要断言 fake runtime 未被调用。

### 面试题 3：当前没有交互式审批 UI 时，`ASK` 为什么应该失败返回，而不是直接执行或直接 deny？

- 用户回答：因为 `ASK` 的语义是“需要用户确认后才能执行”，不是“允许执行”，也不是“永久拒绝”。如果直接执行，就等于系统替用户同意了，权限系统失效。如果直接 deny，又会把“需要确认的中风险命令”和“明确禁止的高风险命令”混在一起，后续无法支持人工审批。
- 标准回答：正确。`ASK` 表达的是“需要人工确认”，不是 `ALLOW`，也不是 `DENY`。当前没有 CLI/UI 审批输入时，最保守且语义准确的行为是返回失败 `ToolResult`，提示 `approval required`，并保证不进入 runtime。直接执行会绕过用户确认；直接 deny 会丢失中风险命令未来可审批执行的语义。后续接入审批 UI 后，`ASK` 可以生成 `ApprovalRequest`，用户批准且请求仍有效时再进入执行链。

## 第 27 天：2026-06-22

### 面试题 1：workspace 边界和 permission gate 分别解决什么问题？为什么一个文件位于 `workspace_root` 内，仍然可能需要 `ASK`？

- 用户回答：workspace 边界负责判断“路径是否在允许目录内”；permission gate 负责判断“这次操作是否危险”。文件即使在 workspace_root 内，覆盖已有文件或删除代码也可能破坏用户工作，所以需要 ASK。
- 标准回答：正确。workspace 边界解决的是“工具是否能访问这个路径”，它防止读取或写入授权工作区之外的文件。permission gate 解决的是“这次具体副作用是否应该直接执行”，它关注覆盖、删除、联网、执行命令等风险。两者不是同一层安全能力：一个文件即使位于 `workspace_root` 内，覆盖已有文件、把代码替换为空字符串、删除大段内容等操作仍可能破坏用户工作，所以应分类为 `ASK`，在没有审批结果时不能静默写盘。

### 面试题 2：请按调用链说明 `write_file` 覆盖已有文件时，从 `ToolRegistry.run(...)` 到最终返回失败 `ToolResult` 之间经过哪些关键函数？为什么测试能证明文件没有被改写？

- 用户回答：调用链是：ToolRegistry.run("write_file", ...) -> Tool.run(...) 参数校验 -> WriteFileTool._run(...) -> _resolve_workspace_path(...) -> _ensure_file_permission(...) -> classify_file_change(...) -> PermissionPolicy.decide(...) -> PermissionError -> ToolRegistry 包装为失败 ToolResult。测试通过检查原文件内容仍是旧内容，证明没有写盘。
- 标准回答：正确。覆盖写入从 `ToolRegistry.run("write_file", arguments)` 开始，registry 找到 `WriteFileTool` 后调用 `Tool.run(...)` 做基础参数校验。随后进入 `WriteFileTool._run(...)`，先通过 `_resolve_workspace_path(...)` 确认目标路径仍在 `workspace_root` 内，再检查 `content` 必须是字符串。真正创建父目录和 `path.write_text(...)` 之前，会调用 `_ensure_file_permission(...)`。这个函数调用 `classify_file_change(tool_name="write_file", path=...)`，因为目标文件已存在，得到 `RiskAssessment(level=ASK, matched_rule="overwrite_existing_file")`；再交给 `PermissionPolicy.decide(...)` 得到 `DecisionAction.ASK`，于是抛出 `PermissionError`。该异常被 `ToolRegistry.run(...)` 捕获并转换成 `ok=False`、`error_type="PermissionError"` 的失败 `ToolResult`。测试不仅检查失败结果，还检查磁盘上的原文件内容仍为旧值，因此能证明拦截发生在写盘前，而不是写盘后才报错。

### 面试题 3：如果后续要支持“用户批准后继续执行这次覆盖写入”，你会如何设计审批恢复链路？

- 用户回答：审批恢复链路应该保存 request_id、工具名、路径、原始参数、风险判断、创建时间、过期时间、文件版本/hash。用户批准后重新检查请求是否过期、文件内容是否变化、路径是否仍在 workspace 内，再执行写入。audit 记录发生了什么；checkpoint/rollback 负责出错后恢复；ASK/DENY 负责执行前是否允许进入副作用路径。
- 标准回答：正确。一个可恢复的审批链路不能只保存“用户点了同意”，还要保存足够多的上下文来确认批准仍对应同一次操作。`ApprovalRequest` 至少应关联 `request_id`、`tool_name`、脱敏后的参数摘要、原始参数或可恢复 payload、`RiskAssessment` / `PermissionDecision`、`workspace_root`、目标路径、创建时间、过期时间，以及文件版本证据，例如 mtime、size、hash 或预期旧内容。用户批准后，执行层应重新校验 request id、审批未过期、路径仍在 workspace 内、当前文件版本仍匹配审批时看到的版本；如果文件在等待期间变化，应拒绝旧审批并要求重新生成请求。`ASK` / `DENY` 负责执行前策略动作，audit 负责记录分类、决策、审批和是否执行的事实，checkpoint/rollback 负责在实际副作用前后提供恢复能力。测试上要覆盖审批过期、文件内容变化、路径变化、request id 不匹配、用户拒绝和用户批准且版本匹配这几类路径，证明旧上下文中的危险写入不会被误执行。

## 第 28 天：2026-06-22

### 面试题 1：audit、log、metrics、trace 分别回答什么问题？为什么 `PermissionAuditEvent` 不应该负责决定 `ALLOW / ASK / DENY`？

- 用户回答：audit 记录“权限相关事实”：谁在什么时间对哪个工具做了什么权限判断，命中了什么规则，最终是否执行，强调可追溯和安全证据。log 记录普通运行过程，比如某个模块启动、某个函数报错、某个文件写入失败，主要服务调试。metrics 记录聚合指标，比如工具调用次数、成功数、失败数、总耗时，回答“整体运行情况如何”。trace 记录一次请求的完整调用链，比如 `user input -> LLM -> tool call -> tool result -> final answer`，回答“一次任务是怎么走完的”。`PermissionAuditEvent` 不应该负责决定 `ALLOW / ASK / DENY`，因为这个职责属于 `PermissionPolicy`。audit 只记录事实，如果 audit 反过来参与决策，就会把“策略判断”和“事实记录”混在一起，后续测试、替换策略、审计回放都会变复杂。
- 标准回答：正确。audit 是安全证据层，重点是可追溯、可回放和可解释；log 是调试事件流，重点是定位运行过程问题；metrics 是聚合数值，重点是趋势、吞吐、失败率和耗时；trace 是单次请求链路，重点是把同一次任务里的 LLM、tool call、tool result 和最终回答串起来。`PermissionAuditEvent` 不能决定 `ALLOW / ASK / DENY`，因为权限动作属于 `PermissionPolicy.decide(...)` 的策略职责。audit 如果参与决策，会造成职责倒置：记录层变成策略层，测试难以判断行为来自 policy 还是 audit，后续替换策略、导出审计或重放事件时也会混乱。正确边界是 policy 先做决策，audit 再记录这次决策和是否执行。

### 面试题 2：从 `tests/test_permissions_audit.py` 出发，说明 `PermissionAuditEvent.to_dict()` 如何把 `datetime` 和 `DecisionAction` 转成稳定 JSON 字段，`append_audit_event(...)` 如何保证一行一个事件。

- 用户回答：`PermissionAuditEvent.to_dict()` 把不能直接稳定写入 JSON 的对象转成普通值：`datetime` 通过 `timestamp.isoformat()` 转成字符串，例如 `"2026-06-22T10:00:00+00:00"`；`DecisionAction` 通过 `action.value` 转成 `"allow"`、`"ask"`、`"deny"`；其他字段如 `tool_name`、`risk_level`、`matched_rule`、`reason`、`executed` 保持普通 JSON 可表示类型。`append_audit_event(path, event)` 确保父目录存在，用 `json.dumps(event.to_dict(), ensure_ascii=False)` 把事件转成一条 JSON 字符串，追加写入文件，并补一个 `\n`。这样每个事件占一行，也就是 JSONL 格式，后续读取时可以逐行 `json.loads(line)`，适合追加、回放和安全审计。
- 标准回答：正确。`tests/test_permissions_audit.py` 固定了当前 audit API 的三个契约：事件字段必须原样保存；`to_dict()` 必须输出稳定 JSON 字段；JSONL 写入必须一行一个事件。`datetime` 不能直接作为稳定 JSON 字段，所以通过 `isoformat()` 转为包含时区的字符串；`DecisionAction` 是枚举对象，写入 JSON 前必须取 `.value`，否则会把 Python 内部对象泄漏到序列化边界。`append_audit_event(...)` 使用 append 模式写文件，并在每次写入后补换行，让多个事件可以不断追加。JSONL 的优势是简单、可流式读取、单行损坏时影响范围小，适合后续 audit replay 和安全矩阵检查。

### 面试题 3：如果后续要把 audit 接入 `ShellCommandTool` 和文件工具 gate，你会在哪一层调用 `append_audit_event(...)`？如何避免记录完整命令输出、文件内容、secret 或 env 值？如果写审计失败，应该阻断工具执行还是降级处理，为什么？

- 用户回答：应该在具体工具的执行前 gate 里调用 `append_audit_event(...)`。对 shell 来说，位置应该在 `ShellCommandTool._run(...)` 中：先 `classify_command(...)`，再 `PermissionPolicy.decide(...)`，构造 `PermissionAuditEvent`，写 audit；如果 `ALLOW` 才进入 `ShellRuntime.run(...)`，如果 `ASK / DENY` 就返回失败，不执行。对文件工具来说，位置应该在 `_ensure_file_permission(...)` 或调用它的 `WriteFileTool._run(...)` / `EditFileTool._run(...)` 附近，因为这里最接近真实写盘动作。为了避免泄漏敏感信息，audit 不应该记录完整命令输出、完整文件内容、完整 env，可以只记录 `tool_name`、`action`、`risk_level`、`matched_rule`、简短 reason、是否执行，后续可以加参数摘要，但要脱敏。
- 标准回答：方向正确，还需要补上审计失败时的策略。短期接入点可以放在最接近副作用的工具 gate：shell 是 `ShellCommandTool._run(...)` 里分类和策略判断之后、进入 `ShellRuntime.run(...)` 之前；文件工具是 `_ensure_file_permission(...)` 或调用它的写盘前边界。长期更理想的是在 `ToolRegistry` 增加可插拔 permission/audit hook，但风险分类仍由具体工具提供，避免 registry 硬编码 shell 或文件语义。审计内容应坚持“记录事实摘要，不记录敏感载荷”：可以记录工具名、动作、风险等级、命中规则、策略原因、是否执行、trace id 或 request id；不能记录完整 stdout/stderr、完整文件内容、完整 env、secret 值或未经脱敏的命令参数。审计写入失败的处理要看风险等级和产品策略：对高风险 `ASK / DENY` 或需要合规留痕的操作，审计失败应阻断执行或至少保持不执行；对低风险 `ALLOW` 操作，可以降级为失败告警或内存缓冲，但不能静默吞掉。当前教学阶段更保守的原则是：权限相关审计失败必须显式暴露，避免系统在没有证据的情况下执行高风险副作用。

## 第 29 天：2026-06-23

### 面试题 1：一个权限系统验收示例为什么必须同时覆盖 `ALLOW`、`ASK` 和 `DENY`？如果只覆盖成功路径，会漏掉什么风险？

- 用户回答：权限系统不是只证明“能执行”，而是要证明三条路径都正确：`ALLOW` 低风险操作能正常执行，不能因为安全系统把正常工作流打断；`ASK` 有风险但不一定禁止的操作，在没有审批 UI 时不能静默执行，必须失败或暂停；`DENY` 明确危险操作必须在真实 runtime 前被拦截，不能进入 `ShellRuntime`。如果只覆盖成功路径，只能证明工具还能跑，不能证明危险命令不会执行，也不能证明需要审批的命令不会绕过用户确认。
- 标准回答：正确。权限系统验收必须同时证明“正常工作不被误伤”和“危险副作用不会绕过边界”。`ALLOW` 路径证明低风险命令仍能进入原执行链路，避免安全层把 Agent 变成不可用；`ASK` 路径证明中风险操作在没有审批结果时不会被系统替用户同意；`DENY` 路径证明明确破坏性操作在真实 runtime 前被拒绝。只覆盖成功路径会留下两个关键盲点：高危命令可能已经进入 runtime 后才失败，中风险命令也可能在没有人工确认时被静默执行。

### 面试题 2：请沿着 `ToolRegistry.run(...) -> ShellCommandTool._run(...) -> classify_command(...) -> PermissionPolicy.decide(...)` 说明 `rm -rf` 为什么不会进入 `ShellRuntime.run(...)`。

- 用户回答：`rm -rf` 会先进入 `ToolRegistry.run`，它找到 `run_command` 对应的 `ShellCommandTool`。`ShellCommandTool._run` 不会马上调用 `ShellRuntime`，而是先调用 `classify_command`。`classify_command` 识别 `rm -rf` 命中 `recursive_delete`，返回 `RiskLevel.DENY`。`PermissionPolicy.decide` 把 `DENY` 风险转换成 `DecisionAction.DENY`。`ShellCommandTool._run` 看到 `DENY` 后直接抛 `PermissionError`。这个异常被 `ToolRegistry.run` 包装成失败 `ToolResult`，所以 `ShellRuntime.run` 根本不会被调用。
- 标准回答：正确。当前执行前 gate 放在 `ShellCommandTool._run(...)` 中。`ToolRegistry.run("run_command", arguments)` 先找到并运行 `ShellCommandTool`；`ShellCommandTool._run(...)` 在调用 `self._runtime.run(arguments)` 前先执行 `classify_command(arguments["command"])`。对于 `["rm", "-rf", ...]`，分类器命中 `recursive_delete`，得到 `RiskAssessment(level=RiskLevel.DENY, matched_rule="recursive_delete")`。随后 `PermissionPolicy.decide(...)` 返回 `PermissionDecision(action=DecisionAction.DENY, ...)`。`ShellCommandTool._run(...)` 对 `DENY` 直接抛出 `PermissionError`，异常被 `ToolRegistry.run(...)` 捕获并转换成失败 `ToolResult`。因此真实副作用边界 `ShellRuntime.run(...)` 不会被调用。

### 面试题 3：如果 Week 5 要加入 checkpoint/rollback，你会把它放在 permission gate 之前还是之后？请说明边界情况、方案对比、如何测试，以及如何证明失败时可以恢复。

- 用户回答：我会把 checkpoint 放在 permission gate 通过之后、真实执行之前。如果放在 permission gate 之前，`DENY` 或未批准的 `ASK` 也会创建无意义 checkpoint，增加噪音。如果放在执行之后，就太晚了，已经无法保证能恢复执行前状态。更合理的链路是：先做风险分类和策略判断；`DENY` 直接拒绝；`ASK` 等用户批准；只有 `ALLOW` 或 `ASK` 被批准后，才在副作用发生前创建 checkpoint，然后执行工具。执行失败或用户要求撤销时，用 checkpoint rollback。边界情况包括：命令访问网络、删除大量文件、修改多个文件、执行到一半失败。不是所有副作用都能 rollback，比如外部网络请求不能靠本地 checkpoint 恢复，所以 Week 5 需要明确 rollback 只覆盖本地 workspace 文件状态。测试上可以构造一个临时 workspace：先写原文件，创建 checkpoint，执行修改，再触发失败或调用 rollback，断言文件内容恢复到执行前。
- 标准回答：正确。checkpoint/rollback 应放在 permission gate 通过之后、真实副作用执行之前。放在 gate 之前会为本来不会执行的 `DENY` 或未审批 `ASK` 创建噪音快照；放在执行之后则失去恢复执行前状态的证据。合理顺序是：风险分类和策略判断先决定是否允许进入副作用路径；`DENY` 不执行也不创建 checkpoint；`ASK` 在未批准前不执行；只有 `ALLOW` 或审批通过后，才创建本地 workspace checkpoint，然后执行文件修改或命令。rollback 的边界必须明确：本地文件状态可以通过 snapshot/git diff 恢复，外部网络请求、远程 API、安装包副作用、后台进程等不能保证自动恢复。测试要覆盖创建快照、修改文件、失败后恢复、多个文件恢复、dirty workspace、以及不可回滚副作用的显式拒绝或降级说明。

## 第 30 天：2026-07-01

### 面试题 1：`Workspace(root)` 和文件工具里的 `_resolve_workspace_path(...)` helper 有什么区别？为什么后续 checkpoint / rollback 更适合依赖 Workspace 对象？

- 用户回答：`Workspace(root)` 是一个可复用的边界对象；`_resolve_workspace_path(...)` 只是文件工具内部 helper。后续 checkpoint / rollback 不只服务文件工具，还要服务 shell、sandbox、快照恢复，所以需要统一的 `Workspace` 作为路径边界事实源，避免每个模块各写一套规则导致漂移。
- 标准回答：正确。`_resolve_workspace_path(...)` 是文件工具内部的局部实现细节，只服务当前 `read_file`、`write_file`、`edit_file` 的路径解析；`Workspace(root)` 是 runtime 层可复用边界对象，可以被 checkpoint、rollback、sandbox、shell runtime 和未来文件工具迁移共享。checkpoint / rollback 需要统一判断“哪些文件属于可恢复的授权工作区”，如果各模块重复写路径规则，就可能出现文件工具允许、checkpoint 不保存，或 shell 认为合法、rollback 无法恢复的边界漂移。`Workspace` 应成为路径归属事实源，permission gate 再负责判断“这次操作是否允许执行”。

### 面试题 2：请从 `Workspace.resolve_path("../outside.txt")` 开始，说明代码如何把相对路径解析成绝对路径，并在哪一步判断它越界。

- 用户回答：`Workspace.resolve_path("../outside.txt")` 会先把输入转成 `Path`。因为它是相对路径，所以拼到 `self.root / "../outside.txt"`，再调用 `.resolve()` 得到真实绝对路径。最后用 `_is_inside(...)` 判断：如果解析后的路径既不等于 `root`，也不在 `root.parents` 关系内，就抛 `ValueError("path is outside workspace")`。
- 标准回答：方向正确，需要把 parents 关系表述得更精确：判断逻辑是“解析后的路径既不等于 `self.root`，并且 `self.root` 不在解析后路径的 `parents` 中”，就说明路径越界。调用链是：`resolve_path(...)` 先用 `_coerce_path(path, label="path")` 拒绝空路径和坏类型；发现输入不是绝对路径后，用 `(self.root / raw_path).resolve()` 消解 `..`、符号链接等路径成分；随后调用 `_is_inside(resolved_path)`。`_is_inside(...)` 返回 `path == self.root or self.root in path.parents`。对于 `../outside.txt`，解析后路径落到 root 的父目录下，不满足该条件，因此抛出 `ValueError`，阻止 workspace 外路径继续进入文件操作。

### 面试题 3：如果 Day 2 要实现 `FileCheckpoint`，它应该如何使用 `Workspace`？哪些文件状态能回滚，哪些副作用不能靠本地 checkpoint 回滚？如何测试这些边界？

- 用户回答：`FileCheckpoint` 应该接收 `Workspace`，所有要保存或恢复的路径都先通过 `workspace.resolve_path(...)` 校验。它能回滚本地 workspace 内文件的内容、创建、删除等文件状态；不能回滚外部命令副作用、网络请求、数据库写入、进程启动、workspace 外文件修改。测试应覆盖：保存后修改文件再恢复、保存后删除文件再恢复、新建文件回滚、越界路径拒绝、workspace 外副作用不被声明为可恢复。
- 标准回答：正确。`FileCheckpoint` 应以 `Workspace` 作为边界输入，创建快照、记录相对路径、恢复文件时都必须先通过 `workspace.resolve_path(...)`，保证 checkpoint 不读取或写回 workspace 外文件。它适合恢复本地 workspace 内的文件内容、文件删除、快照后新建文件的清理，以及多个文件的组合状态；但不能保证恢复网络请求、远程 API、数据库写入、包安装产生的全局副作用、后台进程、系统环境变量变化或 workspace 外文件修改。测试应使用 `tmp_path` 构造隔离 workspace，覆盖文件内容恢复、删除后恢复、新文件 rollback、多个文件恢复、越界路径拒绝，以及明确不可回滚副作用不被 `FileCheckpoint` 宣称为支持范围。

## 第 31 天：2026-07-01

### 面试题 1：`FileCheckpoint.create(workspace, paths)` 为什么必须先调用 `Workspace.resolve_path(...)`？如果 checkpoint 自己重新写路径判断，会带来什么风险？

- 用户回答：`Workspace` 是 runtime 层的路径边界事实源。`FileCheckpoint` 会读取和写回真实磁盘文件，如果不先经过 `Workspace.resolve_path(...)`，就可能把 `../outside.txt`、workspace 外绝对路径、符号链接解析后的外部路径也纳入快照或恢复范围。如果 checkpoint 自己再写一套路径判断，会带来边界漂移：文件工具认为路径合法，checkpoint 认为非法；或者 checkpoint 允许了文件工具本来不允许的路径。这样 rollback 可能漏恢复文件，也可能误删或覆盖 workspace 外文件。正确做法是 checkpoint 只负责保存和恢复文件状态，路径归属统一交给 `Workspace`。
- 标准回答：正确。`FileCheckpoint` 的职责是保存和恢复文件状态，不应该重新定义“哪些路径属于授权工作区”。路径归属必须交给 `Workspace.resolve_path(...)`，这样相对路径、绝对路径、`..`、空路径、坏类型和符号链接解析后的越界情况都使用同一套边界规则。否则会出现边界漂移：文件工具、shell runtime、checkpoint 和未来 sandbox 对同一路径做出不同判断。对 rollback 来说，这种漂移尤其危险，因为它可能造成该保存的文件没有保存，或者 restore 时写回 workspace 外路径。

### 面试题 2：当前 `FileCheckpoint` 如何区分快照时“文件存在”和“文件不存在”？请分别解释修改后恢复、删除后恢复、新建文件清理这三条 rollback 语义。

- 用户回答：创建快照时，每个路径先解析成 workspace 内绝对路径，然后检查 `path.exists()`。如果文件存在，就记录 `existed=True`，并用 `read_bytes()` 保存原始 bytes 内容；如果文件不存在，就记录 `existed=False`，不保存内容。修改后恢复是指快照时文件存在，后来内容被改了，`restore()` 会把原始 bytes 写回去。删除后恢复是指快照时文件存在，后来被删除，`restore()` 会重新创建父目录并写回原始内容。新建文件清理是指快照时文件不存在，后来这个被跟踪路径新建了文件，`restore()` 会删除它，让状态回到当时不存在。
- 标准回答：正确。当前实现记录的是“被跟踪路径在快照时的状态”，不是记录每一步操作日志。`_FileSnapshot` 用 `existed` 表达快照时是否存在，用 `content` 保存存在文件的 bytes 内容。`restore()` 根据 `existed` 分两条路径：快照时存在的文件会被写回原始 bytes，因此能覆盖后续修改，也能重建后续删除；快照时不存在的文件如果后来被创建，则会被删除，恢复到“不存在”的状态。这也是为什么测试必须同时覆盖修改、删除和快照后新建三类场景。

### 面试题 3：如果未来要把 `FileCheckpoint` 接入 `WriteFileTool` 或 `ShellCommandTool`，你会把它放在 permission gate 的哪一侧？如果 restore 过程中失败，应该如何设计错误语义、审计和测试？

- 用户回答：我会把 `FileCheckpoint` 放在 permission gate 通过之后、真实副作用执行之前。合理链路是：tool call -> workspace path resolve -> permission risk classify -> `PermissionPolicy.decide(...)` -> `ALLOW` 或审批通过 -> create `FileCheckpoint` -> 执行真实写文件或 shell 命令 -> 失败或用户撤销时 restore。不能放在 permission gate 之前，因为 `DENY` 或未审批的 `ASK` 本来不会执行，创建 checkpoint 是噪音；也不能放在执行之后，因为那时已经失去执行前状态证据。如果 `restore()` 过程中失败，不能假装回滚成功，应该返回或抛出明确错误，记录哪个 checkpoint、哪个文件失败、是否已经部分恢复、原始错误类型和消息，以及是否需要用户手动介入。审计上应记录 rollback attempt、成功或失败、受影响路径摘要，但不能记录完整文件内容或 secret。测试要覆盖单文件恢复失败、多文件部分恢复、目标路径变成目录、权限不足、恢复失败时原错误被保留，以及 audit/错误结果能让用户知道 workspace 可能处于半恢复状态。
- 标准回答：正确。checkpoint 应放在 permission gate 通过之后、真实副作用之前。`DENY` 和未批准的 `ASK` 不应创建快照，因为没有副作用会发生；执行后再创建则无法保存执行前状态。接入 `WriteFileTool` 时，checkpoint 应在写盘前创建；接入 `ShellCommandTool` 时，要先明确哪些路径会被跟踪，否则 shell 命令可能修改未知文件。restore 失败时要采用显式失败语义，不能把半恢复状态包装成成功。工业级设计还需要 audit 记录 rollback 尝试、结果、路径摘要、trace/request id，并在测试中证明部分恢复、目录冲突、权限错误和原始异常保留都能被调用方观察到。

## 第 32 天：2026-07-01

### 面试题 1：`GitCheckpoint` 和 `FileCheckpoint` 分别适合什么场景？为什么 Day 3 不直接用 `FileCheckpoint` 扫描整个仓库？

- 用户回答：`FileCheckpoint` 适合显式文件列表和普通 workspace 文件状态，例如某个工具准备修改一两个已知文件时，按路径保存 bytes 内容、是否存在，并在失败时恢复这些文件。`GitCheckpoint` 适合 git repo 内的代码修改状态，尤其是 tracked 文件的 dirty tree。Day 3 不直接用 `FileCheckpoint` 扫描整个仓库，是因为递归扫描会带来范围、性能、忽略规则和误删风险：仓库里可能有 `.git`、缓存、虚拟环境、构建产物、大文件和 untracked 文件。git 已经知道哪些文件被跟踪，也知道 tracked 文件相对 index 的差异，所以用 `git diff` 表达 dirty state 更符合代码仓库语义。
- 标准回答：正确。`FileCheckpoint` 是显式文件粒度的本地快照，适合调用方已经知道要保护哪些文件的场景；它不要求目录是 git repo，也不依赖 git 命令。`GitCheckpoint` 是仓库级 dirty diff 快照，适合 Coding Agent 在 git workspace 中保护 tracked 文件修改状态。直接用 `FileCheckpoint` 扫描整个仓库会把“快照哪些文件”的问题变成递归扫描策略问题：要排除 `.git`、依赖目录、构建目录、缓存、大文件、二进制文件和 untracked 文件，还要处理性能和误删风险。git diff 已经把 tracked 文件变化建模为统一 diff，更适合 Day 3 的最小实现。

### 面试题 2：当前 `GitCheckpoint.create(...)` 保存的是哪一种 diff？为什么 restore 要先 `git restore --worktree -- .`，再 `git apply` 保存的 diff？

- 用户回答：当前 `GitCheckpoint.create(...)` 保存的是 `git diff --binary -- .`，也就是 tracked working tree 相对 index 的 dirty diff，不包含 untracked 文件，也不完整表达 staged diff。restore 先执行 `git restore --worktree -- .`，是为了把 tracked working tree 清回 index 状态，移除 checkpoint 创建之后发生的额外修改；然后再 `git apply` 保存的 diff，把工作区恢复到 checkpoint 创建时的 dirty 内容。这样 restore 的目标不是“变干净”，而是“回到创建 checkpoint 的那个 dirty 状态”。
- 标准回答：正确。当前实现保存的是 tracked working tree 相对 index 的 diff：`git diff --binary -- .`。它描述的是“工作区文件内容相对 index 的未暂存变化”。`restore()` 的两步顺序很关键：先 `git restore --worktree -- .` 把 tracked working tree 回到 index，清掉 checkpoint 之后的新修改；再把 checkpoint 保存的 diff 输入 `git apply --whitespace=nowarn -`，重建当时的 dirty state。如果只反向应用某个 diff，可能遇到后续修改冲突；如果只 restore，则会丢掉 checkpoint 创建时本来就存在的 dirty 修改。

### 面试题 3：当前 `GitCheckpoint` 为什么不处理 untracked 文件、staged diff 和 sandbox 外副作用？如果未来要支持这些能力，你会如何扩展测试和错误语义？

- 用户回答：当前 Day 3 只做最小 git diff checkpoint，所以不处理 untracked 文件、staged diff 和 sandbox 外副作用。untracked 文件不在普通 `git diff` 中，需要单独决定是否保存内容、删除策略和忽略规则；staged diff 涉及 index 状态，restore 时要区分 working tree 和 index；sandbox 外副作用例如网络请求、数据库写入、后台进程和 workspace 外文件修改，不属于 git 能恢复的本地文件状态。未来如果要支持这些能力，可以增加 untracked manifest 或 tar/bytes 快照，增加 staged diff 的 `git diff --cached` 保存和 index restore 测试，增加半恢复错误对象，明确哪些路径已恢复、哪些失败、是否需要用户手动处理。测试要覆盖 untracked 文件创建/删除、staged 文件恢复、diff apply 失败、部分恢复、git 命令失败和不可回滚副作用的显式说明。
- 标准回答：正确。当前 `GitCheckpoint` 故意只覆盖 tracked working tree diff，是为了把 Day 3 范围控制在一个可测试的最小语义内。untracked 文件没有进入普通 `git diff`，贸然删除或保存它们可能误删用户临时文件；staged diff 属于 index 状态，和 working tree 状态是两层不同事实；sandbox 外副作用更不属于 git 能表达或恢复的范围。未来扩展应先定义数据模型：untracked 文件可用 manifest 加 bytes 快照或按 ignore 规则选择性纳入；staged diff 可单独保存 `git diff --cached` 并设计 index restore；恢复失败应返回结构化错误，包含失败阶段、git stderr/stdout 摘要、是否已经执行过 restore、是否可能处于半恢复状态和人工处理建议。测试必须覆盖成功恢复、untracked 策略、staged 状态、apply 冲突、部分恢复和不可回滚副作用不被虚假承诺。

## 第 33 天：2026-07-02

### 面试题 1：为什么要先定义 `CommandRuntime` interface，再实现 Docker runtime adapter？

- 用户回答：先定义 `CommandRuntime` interface，是为了先稳定调用方和执行器之间的契约。工具层只需要知道有一个对象能 `run(arguments)` 并返回 `stdout`、`stderr`、`returncode`、`timed_out` 等结构化结果，而不需要知道底层是本地 `ShellRuntime`、fake runtime、Docker runtime 还是远程 sandbox。这样 Docker adapter 只是接口的一个实现，不会反向污染 `ShellCommandTool`、permission gate 或 `ToolRegistry`。如果先做 Docker，很容易把容器检测、挂载、权限、fallback、checkpoint 和 audit 混在一起，接口边界反而不清楚。
- 标准回答：正确。`CommandRuntime` 先于 Docker adapter 的价值是先固定“命令执行器的最小形状”，再替换具体执行环境。工具层和权限层依赖的是稳定抽象，而不是 Docker 细节。`ShellCommandTool` 负责工具 schema 和执行前 permission gate；`CommandRuntime` 负责执行命令并返回结构化结果；Docker adapter 只是未来的一个 `CommandRuntime` 实现。这样可以用 fake runtime 做快速测试，用 `ShellRuntime` 保持当前行为，用 Docker runtime 做隔离执行，而不会让每个调用方都理解容器、挂载和 fallback 细节。

### 面试题 2：现在 `ShellCommandTool` 从收到 `run_command` 参数到调用 fake runtime / ShellRuntime，中间经过哪些层？

- 用户回答：调用链是：`ToolRegistry.run("run_command", arguments)` 先找到 `ShellCommandTool`，然后进入 `Tool.run(arguments)` 做基础参数校验，再进入 `ShellCommandTool._run(...)`。`_run(...)` 先调用 `classify_command(arguments["command"])` 做风险分类，再调用 `PermissionPolicy.decide(...)` 得到 `ALLOW`、`ASK` 或 `DENY`。如果是 `DENY`，直接抛 `PermissionError`，不会进入 runtime；如果是 `ASK`，在没有审批结果时也抛 `PermissionError`；只有 `ALLOW` 才调用 `self._runtime.run(arguments)`。这里的 `_runtime` 类型是 `CommandRuntime`，所以可以是 fake runtime，也可以是默认的 `ShellRuntime()`。
- 标准回答：正确。当前主链是 `ToolRegistry.run(...) -> Tool.run(...) -> ShellCommandTool._run(...) -> classify_command(...) -> PermissionPolicy.decide(...) -> CommandRuntime.run(...)`。`ToolRegistry` 负责查找工具、包装 `ToolResult`、统计和输出截断；`Tool.run(...)` 负责基础参数 schema 校验；`ShellCommandTool._run(...)` 是 shell 工具的执行前 gate；`classify_command(...)` 和 `PermissionPolicy.decide(...)` 决定是否允许进入真实副作用边界；`self._runtime.run(arguments)` 才是真正执行器调用。因为 `self._runtime` 现在按 `CommandRuntime` 注入，fake runtime 只要实现 `run(arguments)` 就能用于测试，默认实现仍是 `ShellRuntime()`。

### 面试题 3：如果未来 Docker 不可用，系统应该如何 graceful fallback？哪些能力可以降级，哪些风险不能静默放行？

- 用户回答：如果 Docker 不可用，系统应该明确报告 sandbox 不可用，而不是让用户以为命令在容器里运行、实际却在宿主机运行。可降级的能力包括：低风险只读命令可以在用户明确允许的情况下回退到 `ShellRuntime`；测试环境可以使用 fake runtime；文档或 dry-run 可以只返回“需要 Docker”错误。不能静默放行的是高风险写文件、删除、安装依赖、网络访问、修改系统状态等操作，尤其是用户要求 sandbox 隔离时，不能自动退回宿主机执行。fallback 必须可见、可测试、可审计。
- 标准回答：正确。graceful fallback 的核心是“清晰失败或显式降级”，不是“偷偷换成宿主机执行”。如果 Docker 不可用，adapter 应返回稳定错误，例如说明 Docker executable 不存在、daemon 不可用或当前环境不支持容器。低风险场景可以由上层策略决定是否改用 `ShellRuntime`，但必须让用户或策略明确知道这是非 sandbox 执行。高风险命令、需要隔离保证的命令、修改 workspace 或系统状态的命令，不能因为 Docker 不可用就静默执行。未来测试要覆盖 Docker 不存在、Docker 命令失败、fallback 错误字段、不会调用宿主机 runtime，以及文档中不把 fallback 误写成完整 sandbox。

## 第 34 天：2026-07-02

### 面试题 1：为什么 Docker adapter 应该实现 `CommandRuntime`，而不是直接改 `ShellCommandTool`？

- 用户回答：Docker adapter 应该实现 `CommandRuntime`，因为 `CommandRuntime` 是命令执行器的统一接口，工具层只需要依赖 `run(arguments)` 和结构化返回值，不应该知道底层是本地 shell、fake runtime、Docker 还是未来远程 sandbox。`ShellCommandTool` 的职责是工具 schema、参数校验后的工具语义，以及执行前 permission gate；Docker adapter 的职责是具体运行环境。如果直接改 `ShellCommandTool`，会把 Docker CLI、镜像、挂载目录、daemon 检测、fallback 语义和权限判断混在一个工具里，后续测试和替换 runtime 都会变困难。让 `DockerRuntime` 实现 `CommandRuntime`，可以保持 `ShellCommandTool` 只依赖抽象，也能用 fake runtime、`ShellRuntime` 和 `DockerRuntime` 复用同一调用边界。
- 标准回答：正确。这里的核心是分层：`ShellCommandTool` 是工具语义边界，`CommandRuntime` 是命令执行边界，`DockerRuntime` 是执行边界的一个实现。Docker 不应该反向污染工具层，否则工具层会同时承担权限、schema、容器参数、运行环境检测和 fallback 策略。通过 `CommandRuntime.run(arguments)`，上层只关心输入输出契约，底层可以替换为本地 shell、fake runtime、Docker runtime 或远程 sandbox。这样后续 Day 6 rollback、audit 和 trace 接入时也有更清楚的插入点。

### 面试题 2：Docker 不可用时为什么不能静默回退到宿主机 `ShellRuntime`？这和 graceful fallback 的区别是什么？

- 用户回答：Docker 不可用时不能静默回退到宿主机 `ShellRuntime`，因为用户或上层策略以为命令会在 sandbox 里执行，实际却在宿主机执行，这会破坏安全边界。比如命令本来应该只修改容器内文件系统，静默回退后可能改到真实工作区、访问真实环境变量、安装依赖或执行危险命令。graceful fallback 的意思是清楚失败或显式降级，例如返回 `sandboxed=False`、`fallback="docker_unavailable"`、稳定的 `returncode` 和错误信息，让上层知道没有隔离执行。静默降级是隐藏事实，graceful fallback 是暴露事实并让调用方做明确决策。
- 标准回答：正确。安全系统最怕“用户以为有隔离，实际没有隔离”。如果 Docker adapter 在 Docker 不可用时偷偷调用 `ShellRuntime`，`sandbox` 这个承诺就变成了假承诺。graceful fallback 必须可见、可测试、可解释：Docker CLI 缺失、daemon 不可用、检查超时都应该返回结构化失败，而不是伪装成容器执行。是否允许改用本地 shell 应该由更上层策略、用户确认或明确配置决定，不能由 adapter 自动偷偷决定。

### 面试题 3：如果 `DockerRuntime.run(...)` 返回 `sandboxed=False` 和 `fallback="docker_unavailable"`，上层调用方应该如何处理？请从安全、用户体验和测试三个角度回答。

- 用户回答：从安全角度，上层应该把这次结果视为“没有 sandbox 执行”，不能继续假设副作用被隔离；对于危险命令、写文件、联网、安装依赖或用户明确要求 sandbox 的任务，应该阻断或要求用户确认，不能自动换成本地 shell。从用户体验角度，应该给出清楚提示：Docker CLI 缺失、daemon 不可用或检查超时，并说明本次命令没有执行在隔离环境中，可以提示用户启动 Docker、安装 Docker，或选择明确的非 sandbox 模式。从测试角度，应该覆盖 fallback 字段、`sandboxed=False`、稳定 returncode、stderr 信息，以及 Docker 不可用时不会调用宿主机 shell；还要测试示例和文档不会把 adapter 误写成完整 sandbox。
- 标准回答：正确。上层处理应该分三层。安全层面，`sandboxed=False` 表示隔离保证不存在，不能继续执行依赖 sandbox 的高风险操作；如果要本地执行，必须经过显式策略或用户确认。用户体验层面，错误要可解释，让用户知道是 Docker 可用性问题，而不是命令本身失败，也要给出下一步选择。测试层面，fallback 是契约：稳定字段、稳定 returncode、不调用宿主机 shell、示例能力边界和文档状态都要被测试或复核。这样才能保证 graceful fallback 不被误用成静默降级。

## 第 35 天：2026-07-02

### 面试题 1：为什么 `DENY` 和未审批 `ASK` 不应该创建 checkpoint？如果它们也创建 checkpoint，会带来什么误导或成本？

- 用户回答：`DENY` 和未审批 `ASK` 都没有进入真实副作用路径，所以不应该创建 checkpoint。`DENY` 表示系统明确禁止执行，未审批 `ASK` 表示需要用户确认但还没有批准；这两种情况下文件不应该被修改，也就没有需要恢复的执行前状态。如果它们也创建 checkpoint，会误导后续维护者以为操作已经被允许或即将执行，还会增加无意义的磁盘读取、状态记录和审计噪音。更严重的是，checkpoint 数量变多后，真正需要 rollback 的执行失败路径会被噪音淹没，permission gate 和 rollback 的职责边界也会混乱。正确顺序应该是：先做风险分类和策略判断，只有 `ALLOW` 或未来审批通过后，才在真实写盘前创建 checkpoint。
- 标准回答：正确。checkpoint 是“已经允许进入副作用路径后的执行前状态证据”，不是所有工具调用都要创建的通用日志。`DENY` 的语义是明确禁止执行；未审批 `ASK` 的语义是暂停并等待用户确认。这两个路径都不应该触碰真实副作用边界，因此也不需要保存可恢复状态。过早创建 checkpoint 会带来三个问题：第一，职责误导，让人以为阻断路径也进入了执行准备阶段；第二，产生额外 I/O 和状态噪音；第三，让 audit、rollback 和 permission gate 的边界难以解释。工业级设计里，permission gate 负责“能不能执行”，checkpoint/rollback 负责“允许执行后失败了如何恢复”。

### 面试题 2：请按调用链说明一次 `EditFileTool` 小范围编辑失败后如何从 permission gate 走到 `FileCheckpoint.restore()`。

- 用户回答：调用链是：`ToolRegistry.run("edit_file", arguments)` 找到 `EditFileTool`，进入 `Tool.run(...)` 做基础参数校验，再进入 `EditFileTool._run(...)`。`EditFileTool._run(...)` 先通过 `_resolve_workspace_path(...)` 解析并确认目标文件在 `workspace_root` 内，然后检查 `old_text`、`new_text` 类型和空值。接着调用 `_ensure_file_permission(...)`，里面用 `classify_file_change(tool_name="edit_file", path=..., old_text=..., new_text=...)` 做文件风险分类，小范围精确替换会得到 `RiskLevel.SAFE` 和 `matched_rule="small_exact_edit"`；`PermissionPolicy.decide(...)` 把它转换成 `DecisionAction.ALLOW`。只有看到 `ALLOW` 后，`EditFileTool` 才读取文件内容、确认 `old_text` 只出现一次，然后调用 `_run_with_file_checkpoint(...)`。这个 helper 用 `Workspace(workspace_root)` 创建工作区对象，再用 `FileCheckpoint.create(workspace, [path])` 保存目标文件执行前状态，随后执行真实 `path.write_text(...)`。如果写盘阶段抛异常，`except` 分支会调用 `checkpoint.restore()` 把文件恢复到写盘前内容，然后继续抛出原始异常，让上层知道这次编辑失败。
- 标准回答：正确。关键点是 checkpoint 创建发生在 permission `ALLOW` 之后、真实写盘之前。当前路径可以拆成六层：`ToolRegistry.run(...)` 负责路由、结构化结果和统计；`Tool.run(...)` 负责基础 schema 校验；`EditFileTool._run(...)` 负责文件工具语义；`_ensure_file_permission(...)` 负责调用 `classify_file_change(...)` 和 `PermissionPolicy.decide(...)`；`_run_with_file_checkpoint(...)` 负责执行前创建 `FileCheckpoint` 并包裹真实写盘；`FileCheckpoint.restore()` 负责把被跟踪文件恢复到快照状态。测试不能只看异常返回，还要断言磁盘上的文件内容恢复为原始内容，才能证明 rollback 真的发生在本地文件状态上。

### 面试题 3：如果未来要支持多文件 patch、shell 命令和 Docker sandbox 的统一 rollback，你会如何拆分 `FileCheckpoint`、`GitCheckpoint`、runtime 和 audit？请说明边界情况、优化思路、方案对比和测试方法。

- 用户回答：我会把职责拆开：`FileCheckpoint` 继续负责显式文件列表的 bytes 快照，适合工具已知会修改哪些文件的场景；`GitCheckpoint` 负责 git repo 中 tracked working tree 的 diff 快照，适合多文件代码 patch 和仓库级 dirty state；runtime 负责执行命令或容器任务，不直接决定权限，也不假装能恢复所有外部副作用；audit 负责记录 permission 决策、checkpoint 创建、执行是否发生、rollback 尝试和结果。对于多文件 patch，如果文件列表明确，可以用 `FileCheckpoint` 包裹所有目标文件；如果是代码仓库级 patch，可以用 `GitCheckpoint` 保存 tracked diff。对于 shell 命令，必须先分析或声明可能修改的路径，否则不能承诺完整 rollback；对于 Docker sandbox，优先让副作用发生在容器或挂载 workspace 内，容器外网络/API、数据库、包安装、后台进程都不能被本地 checkpoint 自动恢复。方案上，保守方案是只对已知文件列表启用 `FileCheckpoint`，安全但覆盖有限；仓库方案是使用 `GitCheckpoint`，适合代码修改但不处理 untracked/staged；sandbox 方案是用 Docker 隔离进程和文件系统，但 Docker 不可用时不能静默降级。测试上要覆盖多文件部分失败恢复、rollback 失败报告、`ASK/DENY` 不创建 checkpoint、shell 命令未知副作用不承诺恢复、Docker 不可用 fallback、不记录 secret 或完整文件内容，以及 audit 能说明执行和 rollback 的真实状态。
- 标准回答：正确。统一 rollback 不应该做成一个“什么都能恢复”的魔法函数，而应该是多个边界的组合。`FileCheckpoint` 适合显式路径和单次文件工具；`GitCheckpoint` 适合 git tracked 文件的仓库状态；runtime 负责运行命令、容器或未来远程 sandbox；audit 负责留下事实证据，包括风险判断、策略动作、是否执行、是否创建 checkpoint、rollback 是否成功。边界情况必须提前说明：untracked 文件、staged diff、workspace 外文件、网络请求、数据库写入、包安装、后台进程和容器外副作用都不能被普通文件 checkpoint 自动恢复。长期优化可以引入 patch plan、路径影响分析、GitCheckpoint staged/untracked 扩展、Docker volume 隔离、rollback audit event 和半恢复错误对象。测试应从行为证明出发：文件内容真的恢复、多文件部分失败可观察、restore 失败不伪装成功、危险操作未获许可不创建 checkpoint、Docker fallback 不调用宿主机 shell、audit 不泄漏完整内容或 secret。

## 第 36 天：2026-07-04

### 面试题 1：`FileCheckpoint` 能恢复什么状态？为什么不能把它宣传成能恢复网络/API、包安装或后台进程副作用？

- 用户回答：`FileCheckpoint` 能恢复的是显式传入路径在 workspace 内的本地文件状态。它会记录文件在 checkpoint 创建时是否存在；如果存在，会保存原始 bytes 内容；如果不存在，会记录不存在状态。恢复时，它能把被修改的文件写回原始内容，能把被删除的文件重新创建出来，也能删除 checkpoint 之后新建的被跟踪文件。它不能恢复网络/API、包安装或后台进程副作用，因为这些副作用不一定表现为 workspace 内某个已跟踪文件的 bytes 内容变化。网络请求可能已经影响远端系统，包安装可能改动全局环境或依赖缓存，后台进程可能持续运行或产生外部状态，这些都不在 `FileCheckpoint` 的数据模型中。把它宣传成完整事务系统会误导用户，以为所有副作用都可撤销；正确表述应该是：它只保证显式跟踪的本地 workspace 文件状态可以恢复。
- 标准回答：正确。`FileCheckpoint` 的恢复范围是“显式文件列表 + workspace 内 + 文件 bytes 状态”。它可以覆盖三类本地文件语义：快照后内容被修改时写回旧内容，快照后文件被删除时重建文件，快照时不存在但后来被创建时删除这个被跟踪路径。它不记录远端 API 调用、数据库写入、pip/npm 安装、系统环境变化、后台进程、workspace 外文件或 Docker 外部副作用。因此它不是通用 rollback、不是事务系统、也不是 sandbox。工业级表达必须把能力和边界同时说清楚：本地文件状态可恢复，外部副作用只能通过 sandbox、审计、补偿操作或人工处理。

### 面试题 2：从 `examples/05_checkpoint_rollback.py` 追到 `Workspace.resolve_path(...)` 和 `FileCheckpoint.restore()`，请说明路径边界和文件恢复分别在哪一层完成。

- 用户回答：在 `examples/05_checkpoint_rollback.py` 中，示例先创建临时 workspace 和 `demo.txt`，然后构造 `Workspace(workspace_path)`，再调用 `FileCheckpoint.create(workspace, [file_name])`。路径边界不由示例自己判断，也不由 checkpoint 重新写一套规则，而是在 `FileCheckpoint.create(...)` 内部对每个 path 调用 `workspace.resolve_path(...)` 完成。`Workspace.resolve_path(...)` 会把相对路径基于 root 解析成绝对路径，并确认解析后的路径仍等于 root 或者位于 root 的 parents 链内，否则抛出越界错误。文件恢复发生在 `FileCheckpoint.restore()`：它遍历保存的 snapshot，如果快照时文件存在，就通过 `_restore_existing_file(...)` 写回原始 bytes；如果快照时文件不存在，就通过 `_restore_missing_file(...)` 删除后来创建的被跟踪文件。也就是说，`Workspace` 负责“这个路径是否属于授权工作区”，`FileCheckpoint` 负责“这个文件状态如何保存和恢复”。
- 标准回答：正确。示例层只负责构造一个可运行场景，不直接承担安全边界。路径边界由 `Workspace.resolve_path(...)` 完成：它校验输入类型和空路径，把相对路径拼到 workspace root 下并 `.resolve()`，再用 `path == root or root in path.parents` 判断解析后路径是否仍在工作区内。`FileCheckpoint.create(...)` 必须复用这个路径边界，避免 checkpoint 和工具各自维护规则导致漂移。恢复层由 `FileCheckpoint.restore()` 完成，它根据 `_FileSnapshot.existed` 分成“写回原 bytes”与“删除快照时不存在的文件”两条路径。这个分层很重要：Workspace 是路径归属事实源，FileCheckpoint 是文件状态恢复机制。

### 面试题 3：如果未来要把 rollback 扩展到多文件 patch、GitCheckpoint 和 shell/Docker runtime，你会如何设计执行顺序、失败报告、审计记录和测试矩阵？

- 用户回答：我会先保持分层，不做一个“万能 rollback”。执行顺序上，先解析 workspace 和风险分类，再由 `PermissionPolicy` 判断；只有 `ALLOW` 或未来审批通过后，才创建合适的 checkpoint，然后执行真实副作用。多文件 patch 如果有明确文件列表，可以创建一个覆盖所有目标文件的 `FileCheckpoint`；如果是 git repo 级代码修改，可以创建 `GitCheckpoint` 保存 tracked dirty diff；shell/Docker runtime 只有在能声明或隔离副作用范围时才承诺 rollback。失败报告要结构化，至少包含原始执行错误、rollback 是否尝试、哪些文件或阶段恢复成功、哪些失败、是否存在半恢复状态，以及用户下一步应该怎么处理。审计记录应包含 trace id、工具名、风险等级、策略动作、checkpoint 类型、是否执行、rollback 尝试和结果，但不能记录完整文件内容、secret 或完整 stdout/stderr。测试矩阵要覆盖：多文件全部恢复、部分写入失败、restore 自身失败、`ASK/DENY` 不创建 checkpoint、GitCheckpoint tracked diff 恢复、untracked/staged 不被误承诺、Docker 不可用 fallback 不调用宿主机 shell、shell 未知副作用不承诺恢复，以及 audit 字段完整且脱敏。
- 标准回答：正确。统一 rollback 应该是分层编排，而不是单个全能函数。推荐顺序是：workspace 边界校验 -> permission 分类和策略 -> 审批通过或 `ALLOW` -> 创建对应 checkpoint -> 执行 runtime/tool -> 失败时恢复 -> 写入结构化 audit。多文件 patch 可用 `FileCheckpoint` 或未来 patch plan；仓库级 tracked 修改可用 `GitCheckpoint`；shell/Docker 需要先解决副作用范围、sandbox 隔离和 audit 事实记录，不能默认承诺恢复所有外部状态。失败报告不能只返回“rollback failed”，而要说明阶段、原始错误、恢复错误、路径摘要、半恢复风险和人工处理建议。测试要从行为出发，证明文件真的恢复、未授权路径不创建 checkpoint、恢复失败可观察、Docker fallback 不静默降级、Git untracked/staged 边界不被误说成已支持、审计不泄漏敏感信息。

## 第 37 天：2026-07-09

### 面试题 1：为什么 Week 6 Day 1 只做 9 维现状评估，而不是直接开始写 retry、audit 或 sandbox 代码？

- 用户回答：Week 6 是加固周，Day 1 的目标是先按工业级 9 个维度把现状、证据、缺口和优先级讲清楚。当前 Week 4-5 已经有 permission gate、Workspace、FileCheckpoint、GitCheckpoint、CommandRuntime、DockerRuntime fallback 和文件 rollback，但这些能力不是完整工业级链路。如果不先评估就直接写 retry、audit 或 sandbox，很容易把未来能力和当前能力混在一起，或者修错优先级。正确顺序是先确认 P0 缺口：安全性、健壮性、可观测性，再把后续 Day 2-Day 7 拆成可测试的小加固项。这样 Day 2 写错误分类、Day 4 写 audit、Day 5 写 safety suite 都有明确依据，而不是凭感觉扩展范围。
- 标准回答：正确。现状评估的价值是建立“事实地图”：哪些能力已经有测试证据，哪些只是独立 API，哪些尚未接入主链，哪些不能对外承诺。加固周不新增大模块，而是把已有 runtime、安全边界和 rollback 做到可解释、可测、可审计。直接写 retry、audit 或 sandbox 会跳过优先级判断，可能把 P1/P2 问题放到 P0 前面，也可能把 Docker adapter 误说成完整 sandbox。Day 1 先产出 9 维差距和 P0/P1/P2 排序，是为了让后续加固都能用测试和文档证明，而不是只靠口号。

### 面试题 2：请沿着 `run_command` 的执行路径说明：一次命令从 `ToolRegistry.run(...)` 到 `ShellRuntime.run(...)` 会经过哪些对象？`ASK` 和 `DENY` 为什么不会进入真实 shell？

- 用户回答：执行路径是：`ToolRegistry.run("run_command", arguments)` 先检查参数是否是 dict，并通过 `get(name)` 找到 `ShellCommandTool`；然后进入 `Tool.run(arguments)`，按 `ToolParameter` 做基础参数校验；接着进入 `ShellCommandTool._run(...)`。在 `_run(...)` 里先调用 `classify_command(arguments["command"])` 得到 `RiskAssessment`，再调用 `PermissionPolicy.decide(assessment)` 得到 `PermissionDecision`。如果结果是 `DecisionAction.DENY`，直接抛 `PermissionError`；如果是 `DecisionAction.ASK`，在没有审批恢复流程前也抛 `PermissionError`；只有 `DecisionAction.ALLOW` 才调用 `self._runtime.run(arguments)`。默认 runtime 是 `ShellRuntime()`，所以真实 shell 只发生在 ALLOW 之后。`ASK` 和 `DENY` 被 `ToolRegistry.run(...)` 捕获后会变成失败的 `ToolResult`，不会继续进入 `ShellRuntime.run(...)`。
- 标准回答：正确。当前主链是 `ToolRegistry.run(...) -> Tool.run(...) -> ShellCommandTool._run(...) -> classify_command(...) -> PermissionPolicy.decide(...) -> CommandRuntime.run(...) / ShellRuntime.run(...)`。`ToolRegistry` 负责工具查找、异常包装、统计和输出截断；`Tool.run(...)` 负责基础 schema 校验；`ShellCommandTool._run(...)` 是 shell 执行前 gate；permission 层只做风险和策略判断，不执行命令。`ASK` 表示需要人工批准但当前尚未接入审批恢复，因此必须失败返回；`DENY` 表示明确阻断。两者都在调用 runtime 之前抛出 `PermissionError`，所以不会触发真实 subprocess。

### 面试题 3：如果要把 audit 自动接入 shell/file gate，你会把写 audit 的逻辑放在哪一层？请说明哪些字段必须记录、哪些字段绝对不能记录、audit 写入失败时如何处理，以及如何测试 allow / ask / deny 三种路径。

- 用户回答：我会把 audit 写入放在具体 gate 附近：shell 侧放在 `ShellCommandTool._run(...)` 做完 `PermissionPolicy.decide(...)` 后，file 侧放在 `_ensure_file_permission(...)` 或它的调用边界附近。这样 audit 能记录真实策略判断，同时不让 `ToolRegistry` 理解 shell/file 的业务风险。必须记录的字段包括 timestamp、trace_id 或后续 request id、tool_name、action、risk_level、matched_rule、reason 摘要、executed、是否创建 checkpoint 或 rollback 结果。绝对不能记录完整命令输出、完整文件内容、secret、token、完整 env 值和大 stdout/stderr。audit 写入失败不能伪装成成功，P0 安全路径更保守：至少要返回可观察的失败或降级字段，避免用户以为已经留证；如果是只读安全命令，未来可以按策略降级，但必须让调用方知道 audit_failed。测试要覆盖 ALLOW 会记录 executed=true 并进入 runtime，ASK 记录 executed=false 且不执行，DENY 记录 executed=false 且不执行；还要测 audit 文件内容脱敏、写入失败语义和不会记录完整文件内容。
- 标准回答：正确。audit 应靠近“事实产生点”，也就是 permission gate 做出 allow / ask / deny 决策的地方，而不是放到低层 runtime 或泛化的 registry 里。runtime 只知道怎么执行，不应该决定安全语义；registry 只知道工具成功失败，不了解 matched_rule 和 executed 的真实含义。必须记录的是可追溯事实：时间、工具名、风险等级、匹配规则、策略动作、是否执行、路径或命令摘要、trace/request id、失败或 rollback 摘要。不能记录完整文件内容、完整 stdout/stderr、secret、token、密码、完整 env、过大的命令输出或用户隐私。audit 写失败时要有明确错误语义，不能静默吞掉；后续可以按策略区分 fail-closed 和 degraded，但必须可测试、可观察。测试应分别构造 ALLOW、ASK、DENY，并断言 audit 事件字段、runtime 是否被调用、敏感内容是否被排除，以及 audit 写失败时调用方能看到稳定错误。

## 第 38 天：2026-07-09

### 面试题 1：为什么 `error_type="PermissionError"` 不足以支撑 retry、audit 和 safety regression？`ToolErrorCode` 解决了什么稳定性问题？

- 用户回答：`error_type="PermissionError"` 只能说明 Python 异常类型，不能稳定表达业务语义。同样是 `PermissionError`，可能是 `DENY`，也可能是未审批的 `ASK`；同样是 `RuntimeError`，可能是普通 runtime 失败，也可能是 checkpoint 或 rollback 失败。如果 retry、audit 或 safety regression 依赖自然语言 `error_message`，后续文案一改测试和策略就会漂移。`ToolErrorCode` 把工具失败变成稳定枚举，例如 `PERMISSION_DENIED`、`PERMISSION_APPROVAL_REQUIRED`、`UNKNOWN_TOOL`、`CHECKPOINT_FAILED`、`ROLLBACK_FAILED`。这样上层可以基于稳定错误码做判断，而不用解析异常名和字符串。
- 标准回答：正确。`error_type` 是语言层异常名，粒度太粗；`error_message` 是给人看的描述，容易随文案和实现细节变化。工业级系统需要机器可依赖的错误语义：是否需要用户审批、是否被策略拒绝、是否是坏参数、是否是未知工具、是否是 runtime 环境失败、是否是 checkpoint 或 rollback 失败。`ToolErrorCode` 把这些失败路径固定成可测试、可审计、可用于策略判断的枚举，同时保留旧 `error_type` / `error_message` 给调试和兼容使用。

### 面试题 2：请说明 `ToolRegistry.run(...)` 捕获异常后如何通过 `ToolResult.from_exception(...)` 得到 `error_code`；ASK、DENY、未知工具、rollback 失败分别映射成什么？

- 用户回答：`ToolRegistry.run(...)` 会先记录开始时间，然后执行参数检查、`get(name)`、`Tool.run(arguments)` 和具体工具逻辑。如果中间抛异常，`except` 分支计算 `duration_ms`，调用 `ToolResult.from_exception(exc, duration_ms=duration_ms)`。`from_exception(...)` 保存原来的 `error_type=type(exc).__name__` 和 `error_message=str(exc)`，同时通过错误分类函数把异常映射成 `error_code`。当前 `ASK` 的错误消息包含 `approval required`，映射为 `ToolErrorCode.PERMISSION_APPROVAL_REQUIRED`；`DENY` 包含 `permission denied`，映射为 `PERMISSION_DENIED`；未知工具是 `KeyError`，映射为 `UNKNOWN_TOOL`；rollback 失败的 `RuntimeError` 消息包含 `rollback failed`，映射为 `ROLLBACK_FAILED`。
- 标准回答：正确。当前统一入口是 `ToolRegistry.run(...)`，它不让异常直接冒泡到 AgentLoop，而是包装成 `ToolResult`。`ToolResult.from_exception(...)` 保留旧字段用于兼容：`error_type` 仍是异常类名，`error_message` 仍是异常文本；新增的 `error_code` 则由异常类型和当前稳定消息标记映射得到。`PermissionError + approval required` 对应 `PERMISSION_APPROVAL_REQUIRED`，`PermissionError + permission denied` 对应 `PERMISSION_DENIED`，`KeyError` 对应 `UNKNOWN_TOOL`，rollback 失败消息对应 `ROLLBACK_FAILED`。这让后续策略层不必直接解析完整自然语言。

### 面试题 3：如果 Day 3 要基于错误码实现 retry policy，哪些错误可以考虑重试，哪些绝对不能重试？请说明边界、反例和测试方式。

- 用户回答：可以考虑重试的应该是明确临时性的 runtime 失败，例如未来定义的超时、Docker daemon 临时不可用、文件锁或外部依赖短暂不可用，但前提是操作没有危险副作用，或者是只读/幂等操作。绝对不能重试的包括 `PERMISSION_DENIED`，因为策略已经禁止；`PERMISSION_APPROVAL_REQUIRED`，因为必须先等用户审批，不能偷偷重试；`INVALID_ARGUMENT` 和 `UNKNOWN_TOOL`，因为参数或工具名本身不对，重复执行不会变好；`ROLLBACK_FAILED` 也不能自动重试，因为系统可能已经处于半恢复状态。`CHECKPOINT_FAILED` 通常也不能直接重试真实副作用，应该先修复 checkpoint 前置条件。测试上应构造 fake runtime 统计调用次数，证明可重试错误按次数重试；同时断言 permission、坏参数、未知工具、rollback 失败都只调用一次或不进入副作用路径，并且不会创建额外 checkpoint。
- 标准回答：正确。retry policy 必须先区分“临时失败”和“策略/输入/安全失败”。可重试候选只应是低风险、幂等、明确临时的失败，例如只读命令超时、临时 runtime unavailable 或未来显式标记的 transient error。不能重试的包括：`PERMISSION_DENIED`（安全策略禁止）、`PERMISSION_APPROVAL_REQUIRED`（需要人类决策）、`INVALID_ARGUMENT`（输入错误）、`UNKNOWN_TOOL`（路由错误）、`ROLLBACK_FAILED`（可能半恢复，继续自动动作会扩大风险）、大多数 `CHECKPOINT_FAILED`（保护机制未建立，不能继续执行副作用）。测试矩阵应覆盖重试次数、幂等操作、非幂等操作不重试、permission 不绕过、rollback failure fail-closed、以及 retry 过程中的 audit/trace 事实记录。

## 第 39 天：2026-07-10

### 面试题 1：为什么 `PERMISSION_DENIED`、`PERMISSION_APPROVAL_REQUIRED` 和 `INVALID_ARGUMENT` 不应该通过 retry 解决？

- 用户回答：这三类失败不是临时运行环境问题，重复执行不会改变根因。`PERMISSION_DENIED` 表示策略明确禁止执行，retry 会绕过安全边界；`PERMISSION_APPROVAL_REQUIRED` 表示需要用户审批，不能由系统偷偷重复尝试；`INVALID_ARGUMENT` 表示输入本身错误，应该修正参数而不是重复执行同一个坏调用。retry 只适合明确临时、低风险、最好是幂等的 runtime 失败。
- 标准回答：正确。retry 解决的是“同一个动作稍后再试可能成功”的临时失败，不解决策略拒绝、用户审批和输入错误。`PERMISSION_DENIED` 是安全策略的最终拒绝，重试会把安全规则变成可绕过规则；`PERMISSION_APPROVAL_REQUIRED` 是 human-in-the-loop 边界，必须暂停等待用户决策；`INVALID_ARGUMENT` 是调用方构造参数有问题，需要修正工具调用。工业级系统必须把这些失败 fail-closed，而不是通过 retry 制造重复副作用。

### 面试题 2：请沿着 `ToolRegistry.run(...) -> ToolResult.from_exception(...) -> ToolResult.error_code -> RetryPolicy.decide(...)` 说明一次工具失败如何变成 retry 决策。

- 用户回答：一次工具调用先进入 `ToolRegistry.run(...)`。如果工具查找、参数校验或具体 handler/runtime 抛异常，`ToolRegistry.run(...)` 会捕获异常并调用 `ToolResult.from_exception(...)`。`from_exception(...)` 保留 `error_type` 和 `error_message`，同时用异常类型和稳定消息标记生成 `ToolErrorCode`，写入 `ToolResult.error_code`。随后调用方把这个 `ToolResult` 交给 `RetryPolicy.decide(...)`。`RetryPolicy` 不解析自然语言，而是读取 `error_code`：如果是 `RUNTIME_FAILED`，返回可重试候选；如果是 permission、参数、未知工具、checkpoint 或 rollback 失败，则返回不可重试并给出原因。
- 标准回答：正确。当前链路把“异常”分两步变成“策略输入”：第一步在 `ToolRegistry.run(...)` 边界把异常包装成 `ToolResult`，避免异常直接打断 AgentLoop；第二步在 `ToolResult.from_exception(...)` 中把粗粒度异常映射为稳定 `ToolErrorCode`。`RetryPolicy.decide(...)` 只消费 `ToolResult`，以 `error_code` 做判断：成功结果不需要 retry，`RUNTIME_FAILED` 是临时失败候选，权限、审批、参数、未知工具、checkpoint 和 rollback 失败默认不可重试。这个设计让 retry policy 不依赖脆弱的错误文本。

### 面试题 3：如果未来要把 retry 真正接入执行链，你会把 attempt loop 放在哪一层？请说明如何避免重复执行危险副作用、如何处理 timeout/backoff、如何记录 audit，以及如何测试 `ROLLBACK_FAILED` 必须 fail-closed。

- 用户回答：我不会把 attempt loop 放进具体工具函数，也不会直接塞进 `ToolResult`。更合适的位置是 `ToolRegistry` 上方或一个独立 `ToolExecutor` / runtime orchestration 层，因为那里能看到工具名、参数、权限结果、幂等性、retry policy、trace 和 audit。为了避免重复危险副作用，执行前必须先判断工具是否只读或显式幂等，写文件、shell、Docker、网络/API、包安装等默认不可自动 retry，除非有 checkpoint、sandbox 或用户确认。timeout/backoff 应该有最大尝试次数、总耗时预算、指数退避或固定退避，并且每次 attempt 都要有独立结果和耗时记录。audit 要记录 trace_id、tool_name、attempt_index、error_code、retry_decision、是否执行、是否被 permission 阻断和最终结果，但不能记录完整 secret、文件内容或大输出。测试上要构造 fake tool 统计调用次数，证明 `RUNTIME_FAILED` 可按策略重试，permission/参数/未知工具不会重试；还要构造 `ROLLBACK_FAILED`，断言 attempt loop 立刻停止、只调用一次、返回 fail-closed，并写出可观察的 audit/reason。
- 标准回答：正确。自动 retry 应该属于执行编排层，而不是单个工具或结果对象。推荐未来新增 `ToolExecutor` 或在 `ToolRegistry` 外包一层 orchestration：它可以读取工具元数据、`ToolResult.error_code`、幂等性、安全级别、trace 和 audit 配置。危险副作用默认不自动 retry；只有只读、幂等、低风险且明确 transient 的失败才允许进入 attempt loop。timeout/backoff 要有 per-attempt timeout、总时间预算、最大次数、退避策略和中断条件。audit 必须记录每次尝试的事实，但保持摘要化和脱敏。`ROLLBACK_FAILED` 的测试必须证明 fail-closed：不再发起下一次 attempt，不创建额外 checkpoint，不继续执行副作用，并返回清晰错误原因。

## 第 40 天：2026-07-10

### 面试题 1：permission policy 与 audit 的职责分别是什么？为什么 `ASK` 和 `DENY` 即使不进入真实执行器，也必须保留审计证据？

- 用户回答：permission policy 负责根据风险评估决定 `ALLOW`、`ASK` 或 `DENY`，属于策略判断；audit 负责记录已经发生的策略事实，属于可追溯证据，不能反过来决定是否允许执行。`ASK` 和 `DENY` 虽然没有进入真实执行器，但它们仍然发生了工具请求、风险匹配和策略决策。如果没有审计，就无法证明系统确实拦截过危险操作，也无法区分“用户请求过但被拒绝”和“工具根本没有被调用”。
- 标准回答：正确。policy 的输入是 `RiskAssessment`，输出是 `PermissionDecision`，它回答“这次调用能否进入副作用路径”；audit 记录决策时间、工具、风险、匹配规则、理由和是否进入执行路径，回答“系统事实上做了什么判断”。`ASK` 与 `DENY` 是安全边界的重要事实：它们可以用于追责、调试、回放、安全回归和发现反复尝试的危险请求。审计不能替代 policy，也不能因为调用未执行就丢失证据。

### 面试题 2：请沿着一次 `run_command` 的 `ALLOW` 路径，说明 `classify_command(...)`、`PermissionPolicy.decide(...)`、`record_permission_decision(...)`、`ShellRuntime.run(...)` 的顺序；为什么 audit 写入失败时 runtime 不得被调用？

- 用户回答：调用先进入 `ShellCommandTool._run(...)`，它调用 `classify_command(...)` 得到 `RiskAssessment`，再把评估交给 `PermissionPolicy.decide(...)` 得到 `ALLOW`。随后调用 `record_permission_decision(...)` 写入摘要 JSONL；只有写入成功后才调用 `ShellRuntime.run(...)`。如果 audit 写入失败仍然调用 runtime，就可能产生真实副作用但没有可追溯证据，安全系统无法证明这次执行是否经过授权，所以当前 `ALLOW` 路径采用 fail-closed。`ASK` 和 `DENY` 则写入 `executed=false` 后继续返回原有 `PermissionError`。
- 标准回答：正确。当前顺序是：风险分类识别 `RiskLevel.SAFE` 和 `matched_rule`；policy 把它映射为 `DecisionAction.ALLOW`；audit helper 仅使用决策摘要构造 `PermissionAuditEvent`；JSONL 成功追加后才进入 `CommandRuntime` / `ShellRuntime`。fail-closed 的原因是把“允许产生副作用”和“至少已有授权事实”绑定起来：审计不可写时继续执行会形成无法解释的安全盲区。该保证只覆盖副作用开始之前的审计写入，不宣称 JSONL 与 shell 本身具备跨系统原子事务。

### 面试题 3：当前 `ALLOW` 能做到 audit fail-closed，但不能让 JSONL、shell 与文件写盘成为一个原子事务。若要继续提高可靠性，你会如何设计事件状态或存储方案？请比较 write-ahead event、事务型数据库/队列、outbox 三种思路，并说明如何测试“副作用成功但完成审计失败”的边界。

- 用户回答：write-ahead event 可以在副作用前先写入“准备执行”事件，优点是简单、适合 fail-closed，缺点是后续执行结果可能缺失，需要补偿或超时扫描；事务型数据库或队列能提供更强的持久化和重试能力，但引入服务依赖、事务边界和运维成本，仍不能天然把本地 shell 与数据库做成一个原子事务；outbox 可以把“待执行/执行结果”放到可靠本地表或队列，再由投递器发送，适合最终一致性，但需要幂等键、状态机和死信处理。当前项目应先保留 write-ahead 摘要事件，未来若需要更强可靠性再引入 outbox 或事务存储。测试要模拟：预写成功后副作用失败、预写失败时副作用不发生、副作用成功后完成事件写入失败、重复投递，以及恢复扫描能把未完成事件标记为 unknown/recovery_required，而不是伪造成功。
- 标准回答：正确。三种方案的核心差异是持久化强度与复杂度：write-ahead event 先记录 intent，再执行副作用，适合当前 fail-closed，但必须接受“执行结果缺失”并设计 reconciliation；事务型数据库/队列提供更强的持久化、重试和查询能力，却不能自动覆盖本地 shell、文件系统和远程 API 的全部原子性；outbox 把待投递事实与业务状态放在同一可靠存储中，再异步投递，适合最终一致性，但必须设计幂等键、状态机、重试上限和死信。测试至少要覆盖 intent 写入失败时零副作用、intent 成功后副作用失败、执行成功但 completion audit 失败、进程崩溃恢复、重复事件去重，以及任何未知状态都不能被标记为成功。当前 Day 4 只实现副作用前的 JSONL fail-closed，未宣称跨系统原子事务。

## 第 41 天：2026-07-10

### 面试题 1：安全回归测试与普通 permission 单元测试的边界是什么？为什么 Day 5 还要新增 `tests/safety/`？

- 用户回答：普通 permission 单元测试主要验证一个分类器或策略函数的局部映射，例如 `classify_command(...)` 是否把 `rm -rf` 判为 `DENY`，以及 `PermissionPolicy.decide(...)` 是否把风险等级映射为 `ALLOW`、`ASK` 或 `DENY`。安全回归测试验证的是跨层安全性质：工具请求经过 `ToolRegistry` 和 gate 后，是否真的没有进入 runtime、文件是否保持不变、audit 是否存在且没有 secret。Day 5 新增 `tests/safety/` 是为了把“决策正确”提升为“决策被执行边界正确地遵守”，防止未来重构时只保留异常断言却意外产生副作用。
- 标准回答：普通 permission 单元测试验证单个风险分类或策略映射的输入输出契约；安全回归测试验证 permission、工具、runtime、workspace、checkpoint 和 audit 之间的组合安全性质。前者可以证明“命令应被拒绝”，后者还必须证明“被拒绝的命令没有调用 runtime、没有修改文件、留下了正确的摘要审计，并且没有泄漏敏感值”。Day 5 的 `tests/safety/` 是独立的回归层，不新增风险规则，而是把跨层安全不变量固定下来，防止调用链重构后出现 gate 绕过或错误地把失败包装成成功。

### 面试题 2：为什么安全测试必须断言“副作用没有发生”，不能只断言异常类型或错误码？

- 用户回答：异常类型和错误码只说明调用方观察到了失败，不说明失败发生在副作用之前。如果 gate 已经调用 runtime 或写盘，之后才抛出 `PermissionError`，系统表面上仍然是失败，但真实文件、网络或进程副作用已经发生。安全测试必须用 `RecordingRuntime.calls == []`、原文件内容、workspace 外 sentinel 和 audit 的 `executed` 字段共同证明失败路径在正确的边界停止。这样才能区分“安全拒绝”和“做完危险动作后才报告失败”。
- 标准回答：错误码是控制流语义，副作用断言是安全事实，两者不能互相替代。一个实现完全可能先执行命令或写入文件，再构造错误结果；此时 `PERMISSION_DENIED` 仍可能出现在返回值中，但系统已经违反 fail-closed 约束。安全回归测试因此要观察执行器调用记录、真实临时文件和外部 sentinel 的内容，并检查 audit 的 `executed` 字段。只有同时证明稳定错误语义、零未授权副作用和正确审计事实，才能证明拒绝路径真正安全。

### 面试题 3：secret redaction 测试如何避免把 secret 本身写进测试失败输出或审计日志？

- 用户回答：测试使用运行时生成的临时 secret，不把固定密钥写进源码。命令只在本地 Python 进程中读取环境变量，不访问网络；断言成功输出等于固定的 `[REDACTED]`，失败时抛出不包含实际输出或 secret 的固定 `AssertionError`。audit 只序列化策略摘要字段，测试检查 JSONL 不包含 secret；如果发现泄漏，也只报告“audit contained a sensitive value”，不把 payload 或 secret 放进 pytest 失败信息。这样测试本身不会成为二次泄漏源。
- 标准回答：secret redaction 测试必须同时保护被测输出、测试代码、audit 和失败报告。推荐使用运行时生成的临时值，避免真实凭据和稳定 token 进入仓库；使用本地、无网络的命令触发真实 `ShellRuntime` 脱敏；成功断言只比较固定脱敏结果；失败分支使用固定错误信息，不能把实际 stdout、stderr、audit payload 或 secret 插入异常消息。对于 audit，应验证它只包含工具名、动作、风险等级、匹配规则、理由和 `executed` 等摘要字段，并用“不包含敏感值”的布尔检查配合固定失败信息。即使实现回归导致泄漏，测试输出也必须保持脱敏。

## 第 42 天：2026-07-10

### 面试题 1：真实小 repo 验证与普通集成测试相比，额外证明了哪些边界？

- 用户回答：真实小 repo 验证使用临时目录中的真实文件、真实工作目录和真实工具组合，证明了路径解析是否落在授权 workspace、修改前后的文件状态、`ReadFileTool`/`EditFileTool`/`ShellCommandTool`/`ToolRegistry` 能否串成闭环，以及测试命令是否真的反馈代码修改结果。普通集成测试通常只验证固定模块协作，未必证明真实 cwd、真实文件内容和实际 subprocess 反馈。它仍然不能证明网络、删除、Git、Docker 或 workspace 外副作用可回滚。
- 标准回答：正确。E2E 额外验证的是跨层事实：真实临时仓库中的 cwd 和路径边界、文件确实发生了预期变化、工具链能完成读取—修改—验证闭环、失败和测试结果能回到 `ToolResult`。它比单元或普通集成更接近用户任务，但仍必须明确临时目录、无真实网络/删除，以及未覆盖的外部副作用边界。

### 面试题 2：为什么局部文件修改成功并通过测试，不能证明 shell、网络和工作区外副作用可回滚？

- 用户回答：`EditFileTool` 的 `FileCheckpoint` 只保存显式跟踪的 workspace 文件状态，能恢复文件内容或删除后来创建的文件；它不记录 shell 进程、网络/API 远端状态、包安装、Git/Docker 或 workspace 外文件。`ShellCommandTool` 只负责 permission gate 和调用 runtime，当前没有通用副作用 rollback。因此局部文件成功与 pytest 通过，只能证明这一条文件路径和测试闭环有效，不能外推到其他副作用。
- 标准回答：正确。`FileCheckpoint` 的数据模型是本地文件快照，`ShellCommandTool` 的职责是命令风险判断和 runtime 转发，两者都没有跨系统事务或补偿操作。测试通过只说明当前仓库状态满足测试，不说明命令产生的进程、网络、环境和外部系统状态可逆。工业级系统必须依靠 sandbox、隔离 runtime、补偿事务或人工处置分别覆盖这些边界。

### 面试题 3：permission 允许、文件写入失败且 rollback 也失败时，报告必须暴露哪些状态？

- 用户回答：报告必须同时暴露原始写入错误和 rollback 错误，返回稳定的 `ROLLBACK_FAILED`，说明 rollback 已尝试但未确认恢复成功，并标记文件状态可能是半恢复或不确定。审计要记录工具、风险动作、是否进入副作用、checkpoint/rollback 尝试和结果摘要，但不能记录完整文件内容或 secret。用户可见结论不能写“已恢复”，而应给出受影响路径摘要、需要人工检查或从版本控制恢复的建议，并停止后续自动副作用。
- 标准回答：正确。该状态必须是 fail-closed：原始错误、恢复错误、阶段、路径摘要、`executed`、checkpoint/rollback 状态和后续处置建议都要可观察；错误码应为 `ROLLBACK_FAILED`，不能降级成普通 runtime failure。系统必须明确“不保证当前文件一致性”，禁止自动 retry 或继续执行，并建议人工检查、对比 diff、从 Git/备份恢复。审计保持摘要化和脱敏，不能伪造成功状态。

## 第 43 天：2026-07-10

### 面试题 1：为什么 run 级 `trace_id` 应由 `AgentLoop` 创建，而不是由每个具体工具自行生成？沿着本次调用链说明它如何进入成功和失败 `ToolResult`。

- 用户回答：run 级 `trace_id` 应由 `AgentLoop` 创建，因为一次 Agent 运行可能包含多轮 LLM、多个工具调用和多个失败/恢复分支，只有入口层创建才能保证整条轨迹共享同一个上下文。如果每个工具自己生成 trace，同一次任务会被拆成互不相干的 trace，无法还原完整调用链。当前链路是 `AgentLoop.run(...)` 创建 `TraceContext`，每个 `ToolCall` 再生成独立 `tool_call_id`，然后调用 `ToolRegistry.run(..., trace_id, tool_call_id)`。`ToolRegistry` 在成功时把两者传给 `ToolResult.success(...)`，在异常时把两者传给 `ToolResult.from_exception(...)`，所以成功和失败结果都能关联到同一 run trace，同时区分具体调用。
- 标准回答：正确。trace 的生命周期应覆盖一次业务运行，而不是某个具体 handler。入口层创建 `TraceContext` 可以把 LLM turn、工具路由、权限判断、runtime 和最终回答挂到同一条链；调用层 id 则区分同一 trace 内的不同工具调用。当前实现沿 `AgentLoop -> ToolRegistry -> ToolResult` 透传 `trace_id`，并为每个 `ToolCall` 生成独立 `tool_call_id`，成功路径使用 `ToolResult.success(...)`，失败路径使用 `ToolResult.from_exception(...)`，且不改变旧的 message 文本和错误码兼容性。

### 面试题 2：当前 trace 透传修补后，为什么仍不能宣称 D1 可观测性“完全达标”？还缺哪些日志、查询和统计证据？

- 用户回答：当前只证明 trace 元数据能从 AgentLoop 传到 ToolResult，并不能证明系统能根据 trace 还原完整事实。还缺结构化 JSON 日志、每个核心对象的时间戳和唯一 id、工具输入输出摘要、耗时和状态记录、按 trace_id 查询完整链路，以及调用次数、成功率、失败率、平均耗时和 P99 等统计。当前 audit 也没有查询接口和远程后端，所以只能说 D1 部分达标。
- 标准回答：正确。字段透传只是可观测性的关联基础，不是完整观测系统。D1 还要求结构化日志、操作时间、输入/输出摘要、耗时、状态、trace 查询、调用统计和 P99 证据；同时要明确敏感信息脱敏和本地 audit 的查询边界。当前项目已经具备部分 trace/error/audit 元数据，但没有完整日志记录器、链路查询和性能统计，因此不能把“有 trace_id”写成“可完整回放”。

### 面试题 3：结合 Week 6 的 9 维证据，你是否允许阶段进入 Week 7 Coding Agent？请给出放行条件、明确阻塞项，以及如果选择放行如何防止后续把占位能力误当成完整 sandbox。

- 用户回答：我允许项目进入 Week 7 的课程切片，但不把 Week 6 宣称为九维全部工业级达标。放行条件是当前全量、E2E、安全集、示例和 compileall 都有证据，permission、audit、workspace、checkpoint/rollback 和 trace 透传边界都写进文档，并把剩余缺口作为显式阻塞项。当前阻塞项包括 retry 还不会自动执行、ASK 不能批准后恢复、audit 没有原子事务和查询、结构化 observability 未完成、Workspace 还不是 shell/file 唯一事实源，以及 Git/Docker/网络副作用没有自动 rollback。后续每个 Coding Agent 模块都必须在文档、schema、示例和测试中明确“当前能力/未实现能力”，禁止把 Docker adapter、局部文件 rollback 或 permission gate 描述成完整 sandbox；涉及危险副作用时继续 fail-closed，并保留 safety/E2E 回归门禁。
- 标准回答：正确。这里的“放行”是带边界的课程推进，不是工业级质量签字。Week 7 可以开始实现 repo scanner，但必须携带 Week 6 的 gap ledger、风险声明和回归测试门禁；未完成的 retry orchestration、审批恢复、审计查询/事务、完整 observability 和跨副作用 rollback 不能被隐式假设为存在。README、每日任务、实现日志、下一步状态和工具 schema 都要保持同一能力边界，任何新增工具先补测试和安全场景，危险动作默认不自动 retry、不绕过 approval，也不能把局部文件 checkpoint 外推成全系统 rollback。
