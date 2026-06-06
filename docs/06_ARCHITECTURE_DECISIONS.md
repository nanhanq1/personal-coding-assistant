# Architecture Decisions

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
