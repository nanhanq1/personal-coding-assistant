# Architecture Decisions

## ADR-0012：Week 3 Day 6 在 ReadFileTool 读取前执行文件资源限制

日期：2026-06-20

### 背景

Week 3 Day 5 已经在 `ToolRegistry` 结果边界实现输出截断，可以防止 shell stdout/stderr 或字符串 payload 过长地写入 `ToolResult` 和 message history。但输出截断发生在工具已经产生结果之后，不能阻止 `read_file` 先把超大文件或明显二进制文件读入内存，也不能给 Agent 一个清晰的“这个资源不适合文本读取”的错误语义。

文件工具当前已经负责 `workspace_root` 路径边界、目录拒绝和文本读取，因此文件大小上限和二进制检测也应该放在文件工具的读取前边界。

### 决策

- 在 `src/pca/tools/file_tools.py` 中新增 `DEFAULT_MAX_READ_FILE_BYTES = 1024 * 1024`。
- `ReadFileTool._run(...)` 在 `path.read_text(...)` 前调用 `_ensure_readable_text_file(path)`。
- `_ensure_readable_text_file(...)` 使用 `path.stat().st_size` 检查文件大小，超过 1MiB 时抛出稳定 `ValueError`。
- `_ensure_readable_text_file(...)` 读取前 1024 字节，发现 NUL 字节时抛出稳定 `ValueError`，作为最小二进制检测。
- 失败仍由 `ToolRegistry.run(...)` 捕获并转换为失败 `ToolResult`，保持 AgentLoop 错误回写兼容。
- `write_file` 和 `edit_file` 本次不改变成功路径。

### 理由

- 文件大小和二进制判断最接近真实文件系统资源，放在 `ReadFileTool` 能在读取前拒绝不适合文本工具处理的资源。
- `ToolRegistry` 适合做统一路由、统计、截断和结果包装，但不应该理解每种工具的文件资源语义。
- Day 5 的输出截断解决“工具结果太长”，Day 6 的资源限制解决“这个文件不应该被文本读取”，两者是不同边界。
- NUL 字节检测不是完整文件类型识别，但足以覆盖最明显的二进制误读风险，符合当前最小可测加固目标。

### 暂不采用

- 暂不实现按项目或按工具动态配置文件大小上限。
- 暂不实现完整 MIME 类型识别、编码探测、图片/压缩包解析或二进制专用工具。
- 暂不实现大文件分块读取、head/tail 读取、日志摘要或语义压缩。
- 暂不把文件拒绝事件写入持久化审计日志；后续 observability 模块再统一接入。

## ADR-0011：Week 3 Day 5 在 ToolRegistry 结果边界执行输出截断

日期：2026-06-20

### 背景

Week 3 Day 5 要解决工具输出撑爆上下文的问题。当前 shell runtime 会返回完整 `stdout`、`stderr`、`returncode` 和 `timed_out`，文件工具会直接返回文件文本；这些原始结果经过 `ToolRegistry.run(...)` 包装成 `ToolResult` 后，会由 `AgentLoop._tool_result_to_message(...)` 写回 message history。

如果大输出不在进入 `ToolResult` 前处理，LLM 看到的 tool observation 可能过长，后续上下文压缩、trace、审计和错误恢复都会受到影响。

### 决策

- 在 `src/pca/tools/base.py` 新增 `truncate_output(text, max_chars=4000)`。
- 在 `src/pca/tools/registry.py` 的成功路径调用 `_truncate_tool_result_payload(...)`。
- 对 shell 返回 dict 中的 `stdout`、`stderr` 分别截断。
- 对 `read_file` 这类字符串 payload 截断。
- 发生截断时设置 `ToolResult.output_truncated=True`。
- 截断文本追加 `[output truncated: kept ...]` 标记，让 LLM 和测试都能看见输出不完整。

### 理由

- `ToolRegistry.run(...)` 是工具结果进入 `ToolResult` 和 message history 的统一边界，能同时覆盖 shell 和文件工具。
- 底层 `ShellRuntime` 保持 raw stdout/stderr，便于低层 runtime 测试、排查和后续 sandbox/runtime 演进。
- `output_truncated` 用结构化字段表达截断状态，比只在自然语言字符串中写“已截断”更可测试、可统计、可审计。
- stdout 和 stderr 分别截断，避免一个通道的大输出挤掉另一个通道的错误信息。

### 暂不采用

- 暂不实现动态 token 预算或按模型窗口自动计算截断上限。
- 暂不保留尾部片段；当前只保留前缀和可见截断说明。
- 暂不把完整原始输出写入文件、数据库或长期 memory。
- 暂不在 `ShellRuntime` 直接返回 `ToolResult`。
- 暂不实现文件大小上限和二进制检测；这些留给 Week 3 Day 6。

## ADR-0010：Week 3 Day 4 在 ToolRegistry 统一记录工具调用统计

日期：2026-06-20

### 背景

Week 3 的工业级加固目标要求工具链路具备初步可观测性。Day 2 已有轻量 `TraceContext` / `AgentEvent` 数据结构，Day 3 已让 `ToolResult` 能携带 trace 元数据，但系统仍无法回答最基础的运行问题：某个工具被调用了多少次、成功多少次、失败多少次、累计耗时是多少。

如果把统计逻辑写进具体文件工具、shell 工具或未来 MCP 工具中，统计口径会分散，未知工具、参数错误和 handler 异常也容易漏记。

### 决策

在 `src/pca/tools/registry.py` 的 `ToolRegistry` 中新增最小 stats：

- 内部 `_stats: dict[str, dict[str, int]]` 保存每个工具的 `calls`、`successes`、`failures` 和 `total_duration_ms`。
- `ToolRegistry.run(...)` 在成功和失败路径统一调用 `_record_stats(...)`。
- handler 抛错、参数校验失败和未知工具调用都计入失败统计。
- 未知工具按请求的工具名记录 stats，便于后续发现 LLM 生成了不存在的 tool name。
- `get_stats()` 返回统计快照，不暴露内部可变对象。
- `clear()` 同时清空注册工具和统计状态。

### 理由

- `ToolRegistry.run(...)` 是 `AgentLoop` 面向工具系统的统一入口，能覆盖成功、失败、未知工具和参数错误。
- 统计属于聚合指标，不应该污染具体工具的业务逻辑。
- 返回快照可以避免外部调用方篡改内部统计，保持接口边界清晰。
- 当前只记录最小整数指标，避免过早引入 metrics SDK、持久化或复杂 logger hook。

### 暂不采用

- 暂不实现 logger hook 或 OpenTelemetry exporter。
- 暂不把 stats 写入文件、数据库或长期 memory。
- 暂不记录参数内容，避免提前引入隐私和脱敏边界。
- 暂不把 stats 和 trace 合并；stats 是聚合指标，trace 是单次调用链路。

## ADR-0009：Week 3 Day 3 以默认字段扩展 ToolResult 元数据

日期：2026-06-19

### 背景

Week 3 Day 2 已经新增 `TraceContext` 和 `AgentEvent`，但工具执行结果仍只能表达成功/失败内容和耗时。后续要把一次 Agent 运行、一次工具调用和输出截断状态串成可观测轨迹，需要先让 `ToolResult` 能稳定保存这些元数据。

同时，`ToolResult.__str__()` 已被 `AgentLoop` 用于写回 message history。如果新增字段改变字符串输出，就会破坏旧示例、旧测试和未来 LLM 看到的工具结果文本。

### 决策

扩展 `src/pca/tools/base.py` 的 `ToolResult`：

- `trace_id: str | None = None`，用于标识一次 Agent 运行或调用链。
- `tool_call_id: str | None = None`，用于标识一次具体工具调用。
- `output_truncated: bool = False`，用于标识工具输出是否被截断。
- `ToolResult.success(...)`、`ToolResult.failure(...)` 和 `ToolResult.from_exception(...)` 支持这些可选关键字参数。
- 保持旧调用方式兼容，保持 `ToolResult.__str__()` 输出不变。

### 理由

- 默认值让旧测试、旧示例和旧调用方式不需要同步修改。
- 把截断状态作为结构化字段保存，比只把“已截断”写进字符串更利于测试、统计和后续审计。
- `trace_id` 和 `tool_call_id` 分开保存，避免把“一次任务链路”和“一次工具调用”混成同一个粒度。
- Day 3 只扩展结果信封，不要求 `AgentLoop` 自动创建或传入 trace，降低主链改动风险。

### 暂不采用

- 暂不在 `AgentLoop` 中自动生成 `TraceContext`。
- 暂不在 `ToolRegistry.run(...)` 中自动生成 `tool_call_id` 或统计调用次数。
- 暂不实现实际输出截断；Day 5 再把 shell/file 输出截断接入具体边界。
- 暂不改变 message history 为 JSON 或事件流格式。

## ADR-0008：Week 3 Day 2 先在 core 层定义轻量 trace 事件模型

日期：2026-06-18

### 背景

Week 3 的加固目标包含 trace、调用统计、输出截断和资源边界。当前主链已经有 `AgentLoop`、`ToolRegistry`、`ToolResult`、文件工具和 `ShellRuntime`，但还没有一个可在线路中传递的 trace 上下文，也没有可复用的事件数据结构。

如果直接在 `AgentLoop`、`ToolRegistry` 或 `ShellRuntime` 中散落字符串日志，后续很难把同一次用户请求、LLM 决策、工具调用、工具结果和错误恢复串成可回放轨迹。因此需要先定义最小数据结构，再逐步接入各层。

### 决策

新增 `src/pca/core/events.py`：

- `TraceContext(trace_id: str)` 表示一次 Agent 调用链共享的 trace 上下文。
- `TraceContext.new()` 使用 `uuid4().hex` 生成新的非空 trace id。
- `AgentEvent(event_type: str, trace_id: str, payload: dict[str, object])` 表示一条轻量事件。

本次只新增数据结构和单元测试，不改 `AgentLoop`、`ToolRegistry`、`ToolResult` 或 observability logger。

### 理由

- `core/events.py` 位于 Agent Loop 和 Tool Runtime 都能引用的低层边界，适合放跨调用链数据结构。
- 先用轻量 dataclass，避免在 Week 3 Day 2 过早引入 OpenTelemetry SDK、事件流、持久化或复杂继承树。
- `payload` 先保留为 dict，能承载后续工具名、参数摘要、错误信息、截断标记和统计字段，同时不绑定具体事件类型。
- 不提前接入主链，可以保持当前 95 个测试和示例兼容，再在 Day 3/Day 4 逐步把 trace 字段接入 `ToolResult` 和 `ToolRegistry`。

### 暂不采用

- 暂不实现 span、parent_id、timestamp、duration 或采样。
- 暂不把 `Message` 或 `ToolResult` 改成事件流格式。
- 暂不接入 `src/pca/observability/logger.py`，该目录当前仍是占位。
- 暂不引入 OpenTelemetry SDK；后续需要外部导出时再评估。

## ADR-0007：第 2 周 Day 4 在 ToolRegistry 边界返回结构化 ToolResult

日期：2026-06-12

### 背景

第 1 周和第 2 周前半段的工具结果主要依赖裸返回值和异常：

- 文件工具成功时返回字符串，例如 `"ok"` 或文件内容。
- shell runtime 成功时返回 dict，例如 `stdout`、`stderr`、`returncode` 和 `timed_out`。
- 工具失败时抛异常，再由 `AgentLoop` 转成一段错误字符串。

这种方式能跑通最小闭环，但不利于后续 LLM adapter、可观测性、错误恢复和测试稳定性。调用方很难统一判断一次工具调用是成功、失败、参数错误、运行时错误还是未知工具。

### 决策

新增 `ToolResult`，并把结构化结果放在 `ToolRegistry.run(...)` 边界：

- `ToolResult.ok` 表示工具调用是否成功。
- `ToolResult.result` 保存成功时的原始工具返回值。
- `ToolResult.error_type` 保存失败时的异常类型名称。
- `ToolResult.error_message` 保存失败时的异常消息。
- `ToolResult.duration_ms` 保存工具路由和执行耗时。
- `ToolRegistry.run(...)` 捕获查找、参数校验和 handler/runtime 执行中的异常，并返回失败 `ToolResult`。
- `Tool.run(...)` 暂时保持原始返回值和异常语义，避免一次性改动所有具体工具测试和低层工具 API。
- `ToolResult.__str__()` 保持现有 `AgentLoop` message history 兼容：成功时写回原结果文本，失败时写回 `Tool execution failed: ...`。

### 理由

- `ToolRegistry.run(...)` 是 `AgentLoop` 面向工具系统的统一入口，最适合作为结构化结果边界。
- 保留 `Tool.run(...)` 的低层语义，可以让文件工具和 shell runtime 的直接单元测试继续验证真实工具行为。
- `ToolResult` 先解决“结果信封”问题，为后续 trace id、审计日志、错误分类、权限审批和真实 LLM adapter 留出扩展点。
- 兼容旧的 message history 文本格式，避免 Day 4 一次性大改 AgentLoop、示例和全部工具测试。

### 暂不采用

- 暂不把 `Tool.run(...)` 全面改成返回 `ToolResult`。
- 暂不把 `Message.content` 改成 JSON payload 或专门的 tool result schema。
- 暂不实现 trace id、重试策略、权限审批、sandbox 或 checkpoint / rollback。
- 暂不接真实 LLM adapter；当前继续用 mock LLM 和测试证明工具边界。

## ADR-0006：第 2 周 Day 1 使用 ToolParameter 声明工具参数 schema

日期：2026-06-09

### 背景

第 1 周的 `Tool` 已经包含 `name`、`description` 和 `handler`，`ToolRegistry` 也能统一注册和执行工具。但真实 LLM adapter 需要更结构化的工具说明，才能知道每个工具需要哪些参数、参数类型是什么、哪些字段必须提供。

如果只依赖自然语言描述，模型容易生成错误参数；如果只在具体工具里做校验，错误会下沉到工具实现内部，调用边界不够清晰。

### 决策

新增 `ToolParameter` 并扩展 `Tool`：

- `ToolParameter` 描述单个参数的名称、JSON 类型、说明和是否必填。
- `Tool.parameters` 保存工具参数声明。
- `Tool.to_schema()` 导出接近 JSON Schema 的工具描述。
- `Tool.run(...)` 在调用 handler 前统一校验必填字段和基础类型。
- `ToolRegistry.list_tool_schemas()` 统一导出所有已注册工具 schema。
- 内置 `read_file`、`write_file` 和 `run_command` 都声明参数 schema。

### 理由

- 让工具系统更接近真实 tool calling 接口。
- 让未来 LLM adapter 可以从注册表直接获得工具列表。
- 将基础参数校验前移到 `Tool.run(...)`，避免坏参数进入具体工具。
- 保持具体工具继续负责业务语义和安全边界，例如路径越界、命令工作区、超时和危险操作。

### 暂不采用

- 暂不引入 Pydantic，避免第 2 周 Day 1 过早增加依赖和抽象。
- 暂不实现完整 JSON Schema 校验器，只实现当前项目需要的基础类型和必填校验。
- 暂不关闭 `additionalProperties`，避免过早限制未来工具扩展字段和 trace 字段。
- 暂不把 schema 当成权限系统；危险命令审批留到第 3 周 Permission System。

## ADR-0005：工业级加固必须先处理输入校验、错误回写和密钥边界

日期：2026-06-06

### 背景

本次对当前所有已实现代码进行审查时发现，核心运行路径已经能完成最小 Agent Loop、文件工具和 shell runtime，但仍存在工业级边界不足：

- 早期 Responses API 实验脚本把 API key 硬编码在源码中，并在模块导入时创建真实 client。
- `Tool`、`ToolRegistry`、`Message` 和 `ToolCall` 对外部输入缺少结构校验。
- `AgentLoop` 遇到工具失败时会直接抛异常，LLM 无法基于错误信息恢复。
- 文件工具和 shell runtime 对目录、工作区根目录、环境变量和超时上限的校验还不完整。

### 决策

- API 实验脚本只能惰性创建 client，密钥必须来自 `PCA_OPENAI_API_KEY` 或 `OPENAI_API_KEY` 环境变量。
- 正式源码中不得出现硬编码 API key；新增测试扫描 `src/` 下的 Python 文件防止回归。
- `Tool`、`ToolRegistry`、`Message`、`ToolCall` 和 `ScriptedLLM` 在边界处做类型和结构校验。
- `AgentLoop` 对工具执行异常进行捕获，并把错误作为 `role="tool"` 的消息写回 `message history`，让 LLM 有机会恢复。
- 文件工具要求 `workspace_root` 是已存在目录，读取目录时抛稳定的 `IsADirectoryError`，写入内容必须是字符串。
- shell runtime 要求 `workspace_root` 和 `cwd` 都是已存在目录，限制 `timeout_seconds` 上限，并拒绝空环境变量名。
- 修改前代码快照保存在 `docs/code_reviews/2026-06-06-before-industrial-refactor/`，其中旧版敏感 key 已脱敏。

### 理由

- Agent 接收的参数最终来自 LLM 或用户输入，不能默认可信。
- 工具失败是 Agent 正常运行的一部分，保留错误轨迹比直接中断更利于恢复和调试。
- API key 属于凭据，不应出现在源码、测试或备份快照中。
- 运行前校验能把平台相关异常转换为稳定、可测试、可解释的错误语义。

### 暂不采用

- 暂不提前实现完整权限系统、风险分类器和审批流；这些仍留到第 3 周。
- 暂不把 Responses API 实验脚本升级为正式 LLM adapter；当前主路径继续使用 mock LLM。
- 暂不实现完整 sandbox、进程树清理和命令 allowlist；这些仍属于后续 runtime 模块。

## ADR-0004：第 1 周 Day 4 shell runtime 先实现受工作区限制的同步命令执行

日期：2026-06-06

### 背景

Day 4 开始实现 shell runtime。相比文件工具，shell 命令可以执行任意程序、访问环境变量、创建文件、删除文件或长时间运行，因此必须先定义最小安全边界。

### 决策

新增 `ShellRuntime`、`ShellCommandTool` 和 `run_command(arguments)`：

- 必须提供 `command`、`workspace_root` 和 `timeout_seconds`。
- `cwd` 可选，默认相对于 `workspace_root` 的当前目录。
- 相对 `cwd` 以 `workspace_root` 为基准解析。
- 解析后的 `cwd` 必须位于 `workspace_root` 内，否则抛 `ValueError`。
- `command` 支持字符串和 `list[str]` 两种形式。
- 字符串命令继续使用 `shell=True`，用于兼容早期测试和简单 shell 内置命令。
- 列表命令使用 `shell=False`，作为推荐形式，用于避免手写 shell 引号、减少参数解析歧义和 shell 注入风险。
- 命令执行逻辑位于 `src/pca/runtime/shell_runtime.py`，通过 `subprocess.run(...)` 同步执行。
- `ShellCommandTool` 位于 `src/pca/tools/shell_tools.py`，只负责把工具调用转发给 runtime。
- `timeout_seconds` 会被规范化为正浮点数后再传给 `subprocess.run(...)`。
- 参数校验错误直接抛 `ValueError`，不伪装成命令执行失败。
- 返回值包含 `stdout`、`stderr`、`returncode` 和 `timed_out`。
- 超时时返回 `returncode=-1` 和 `timed_out=True`。

### 理由

- 让 Day 4 先具备可测试的最小 runtime 行为。
- 保留命令输出、错误输出、退出码和超时状态，方便后续 Agent 判断下一步。
- 将工作目录边界前置，避免 shell 命令默认在未授权目录中执行。
- 保持 runtime 层和 tool 层分离，后续可以把本地 runtime 替换为 sandbox、docker 或远程 runtime。
- 与 Python `subprocess` 官方建议保持一致：优先传入参数序列，让 subprocess 负责必要的转义和引用。
- 为后续权限系统、危险命令检测、审计日志和 sandbox runtime 留出扩展点。

### 暂不采用

- 暂不实现危险命令审批。
- 暂不实现异步命令和流式输出。
- 暂不实现进程树清理。
- 暂不实现跨平台 shell 解析抽象。

## ADR-0003：第 1 周 Day 3 文件工具必须限制在 workspace_root 内

日期：2026-06-04

### 背景

Day 3 开始实现 `read_file` 和 `write_file`。文件工具是 Coding Agent 的第一类真实能力，但如果工具直接接受任意路径，就可能读取或覆盖工作区外的文件。

### 决策

文件工具统一通过 `_resolve_workspace_path(arguments)` 解析路径：

- `arguments["path"]` 是要读写的目标路径。
- `arguments["workspace_root"]` 是允许读写的工作区根目录；未传入时默认使用当前工作目录。
- 相对路径先拼到 `workspace_root` 下再解析。
- 绝对路径必须仍然位于 `workspace_root` 内。
- 路径越界时抛出 `ValueError`。
- `write_file` 写入嵌套路径时会自动创建缺失的父目录。

### 理由

- 让文件工具从第一天开始具备基本安全边界。
- 让测试可以用 `tmp_path` 构造隔离工作区，不污染真实项目文件。
- 为后续权限系统、审计日志和 workspace abstraction 留出清晰接入点。
- 区分“非法路径”和“文件不存在”两类错误，方便 Agent 后续做恢复策略。

### 暂不采用

- 暂不实现完整权限审批。
- 暂不实现文件编辑 diff。
- 暂不实现二进制文件处理。

## ADR-0002：第 1 周 Day 2 使用 ToolRegistry 管理工具调用

日期：2026-06-01

### 背景

Day 1 的 `AgentLoop` 直接接收 `dict[str, callable]`。这种方式能完成最小闭环，但随着工具数量增加，会缺少统一的工具元数据、注册入口、错误处理和执行边界。

### 决策

新增 `Tool` 和 `ToolRegistry`：

- `Tool` 负责包装单个工具的名称、描述和 handler。
- `ToolRegistry` 负责注册、查找和执行工具。
- `AgentLoop` 只调用 `ToolRegistry.run(tool_call.name, tool_call.arguments)`，不直接依赖具体工具函数。

### 理由

- 让 Agent Loop 保持简单，只关注 LLM 消息和工具调用流程。
- 为后续文件工具、shell 工具、权限系统和工具 schema 留出扩展点。
- 让未知工具、重复注册等错误集中在工具系统内部处理。
- 更接近真实 Coding Agent 的工具路由结构。

### 暂不采用

- 暂不实现 JSON Schema 参数校验。
- 暂不实现异步工具。
- 暂不实现权限审批和危险工具拦截，这些留到后续模块。

## ADR-0001：第 1 天使用 mock LLM 而不接入真实 API

日期：2026-05-26

### 背景

当前目标是理解并实现最小 Agent Loop，而不是测试模型能力或 API 接入。

### 决策

使用可脚本化的 mock LLM 来稳定地产生 tool call 和最终回答。

### 理由

- 初学阶段更容易观察 Agent Loop 的控制流。
- 测试可重复，不受网络、API key、模型输出随机性影响。
- 后续可以把 mock LLM 替换为真实 LLM adapter，而不改 Agent Loop 的主结构。

### 暂不采用

- 暂不接入真实 OpenAI / Anthropic API。
- 暂不实现复杂 tool schema。
- 暂不实现多轮规划、权限和 RAG。
