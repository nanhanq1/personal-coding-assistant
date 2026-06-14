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
