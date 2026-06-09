# Architecture Decisions

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
