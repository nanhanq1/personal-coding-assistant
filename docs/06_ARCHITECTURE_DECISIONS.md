# Architecture Decisions

## ADR-0028：Week 6 Day 7 在 AgentLoop 入口创建并透传 trace metadata

日期：2026-07-10

### 背景

`TraceContext` 和 `ToolResult` 的 trace 字段已经存在，但此前没有接入 `AgentLoop` 主链。若每个工具自行生成 trace，同一次用户任务会被拆成多个无法关联的局部轨迹；若只依赖错误文本，也无法稳定区分同一 run 内的多个工具调用。

### 决策

- `AgentLoop.run(...)` 为一次运行创建一个 `TraceContext`，并在 `AgentLoopResult` 暴露 `trace_id`。
- 每个 `ToolCall` 生成独立 `tool_call_id`。
- `ToolRegistry.run(...)` 接受可选的 `trace_id` / `tool_call_id`，并将它们保留到成功或失败 `ToolResult`。
- 保持旧的 `Message` 文本、错误码、直接调用 `ToolRegistry.run(name, arguments)` 的兼容性。

### 理由

- 入口层拥有完整的 run 生命周期，能把 LLM turn、工具路由和失败恢复关联到一条轨迹。
- 调用级 id 可以在同一 trace 内区分连续或批量工具调用。
- 这只是可观测性关联基础，不宣称已经具备结构化日志、trace 查询、远程 audit 或 P99 统计。

### 暂不采用

- 暂不在本 ADR 中实现自动 retry、结构化 logger、trace 查询 API 或 OpenTelemetry 导出。
- 暂不修改 `Message` 为事件流或 JSON payload。

## ADR-0027：Week 6 Day 4 在 permission gate 自动写入摘要审计，ALLOW 路径 fail-closed

日期：2026-07-10

### 背景

`PermissionAuditEvent` 与 JSONL 追加函数已经存在，但 shell/file gate 不会自动调用它。因而 `ALLOW`、`ASK`、`DENY` 虽有策略结果，却缺少可测试的统一证据；更严重的是，允许路径如果不能持久化审计，就无法证明副作用曾获授权。

### 决策

- 新增 `record_permission_decision(...)`，只从 `PermissionDecision` 构造摘要事件。
- shell、write_file、edit_file 在 `PermissionPolicy.decide(...)` 后、真实副作用前写入审计。
- 事件仅含 `timestamp`、`tool_name`、`action`、`risk_level`、`matched_rule`、`reason`、`executed`；禁止写入命令、路径、文件内容、env、token、secret、stdout、stderr。
- `executed=True` 表示 permission gate 已允许进入副作用路径，不表示 runtime 或写盘必然成功。
- `ALLOW` 的 audit 写入失败必须阻止 runtime/checkpoint/写盘；`ASK` 与 `DENY` 的写入失败仍保留原始 `PermissionError`，且绝不执行。
- 调用方可注入 `audit_path` 以隔离测试或指定存储；shell 默认写到进程工作目录 `.pca/permission-audit.jsonl`，避免从未验证或只读的 `workspace_root` 派生路径而改变 runtime 校验语义。
- `.pca/` 是本地运行时审计目录，加入 `.gitignore`。

### 理由

- 把审计放在 gate 边界，能同时覆盖 shell/file 的 allow、ask、deny，而不让 runtime、checkpoint 或 policy 承担混合职责。
- 允许路径先落审计再产生副作用，提供最小 fail-closed 保证。
- `ASK` 与 `DENY` 不产生副作用；保留它们原有错误语义比把存储故障伪装成策略结果更清晰。
- 默认 audit 不依赖用户传入的工作区，可保持 `workspace_root`、`cwd` 的既有校验顺序和错误契约。

### 暂不采用

- 暂不实现跨 JSONL、shell、文件系统的原子事务；副作用开始后的失败仍由现有 runtime/checkpoint 边界表达。
- 暂不实现审批通过后恢复执行、审计查询 API、远程后端或 trace 关联。
- 暂不新增文件 `DENY` 风险规则；测试通过注入策略覆盖该 gate 分支。

## ADR-0026：Week 6 Day 3 RetryPolicy 只表达可重试语义，不自动重复执行工具

日期：2026-07-10

### 背景

Week 6 Day 2 已经在 `ToolResult` 边界新增 `ToolErrorCode`，让工具失败不再只依赖 `error_type` 和自然语言 `error_message`。Day 3 需要在这个稳定错误码之上定义 retry policy，但当前工具系统已经具备文件写盘、shell 执行、permission gate 和 rollback 等副作用路径。

如果直接在 `ToolRegistry.run(...)` 中自动重试，会让 `write_file`、`edit_file` 或 `run_command` 这类工具可能重复执行危险副作用；如果继续让上层只读错误消息，又无法稳定区分临时 runtime 失败和绝对不可重试的权限、参数或 rollback 失败。

### 决策

- 新增 `src/pca/tools/retry.py`。
- 定义 `RetryDecision(retryable: bool, reason: str)`，让策略输出同时包含布尔判断和解释原因。
- 定义 `RetryPolicy.decide(result: ToolResult) -> RetryDecision`。
- 定义便捷函数 `should_retry(result, policy=None) -> bool`。
- `RetryPolicy` 只接受 `ToolResult`，拒绝含糊对象。
- 成功结果不可重试。
- `RUNTIME_FAILED` 作为可重试候选，表达“可能是临时失败”。
- `INVALID_ARGUMENT`、`UNKNOWN_TOOL`、`PERMISSION_DENIED`、`PERMISSION_APPROVAL_REQUIRED`、`CHECKPOINT_FAILED` 和 `ROLLBACK_FAILED` 默认不可重试。
- `CHECKPOINT_FAILED` 默认不可重试，因为恢复保护不可用时继续执行会扩大风险。
- `ROLLBACK_FAILED` 必须 fail-closed，不能自动再次扩大副作用。
- 从 `pca.tools` 包入口导出 `RetryDecision`、`RetryPolicy` 和 `should_retry`。

### 理由

- retry policy 属于策略判断，不属于 `ToolResult` 结果信封，也不属于 `ToolRegistry` 执行循环。
- 独立模块能让 Day 3 focused tests 直接证明策略边界，不改变现有工具行为。
- 以 `ToolErrorCode` 为输入，避免解析自然语言错误消息。
- 返回 `RetryDecision` 比只返回布尔值更适合后续 audit、debug 和面试讲解。
- 当前只做“是否可重试”的语义判断，给后续 timeout/backoff/executor 留接口，但不提前实现自动循环。

### 暂不采用

- 暂不在 `ToolRegistry.run(...)` 中自动 retry。
- 暂不重复执行 `write_file`、`edit_file`、`run_command` 或任何带副作用工具。
- 暂不实现 backoff、sleep、最大尝试次数、jitter 或 circuit breaker。
- 暂不把 retry 决策自动写入 audit JSONL。
- 暂不把 timeout policy 从 `ShellRuntime` 中抽象为全局运行时策略。

## ADR-0025：Week 6 Day 2 在 ToolResult 边界增加稳定错误码

日期：2026-07-09

### 背景

Week 4-5 已经接入 shell/file permission gate、`CommandRuntime`、`DockerRuntime` graceful fallback、`FileCheckpoint`、`GitCheckpoint` 和文件工具局部 rollback。但工具失败仍主要依赖 `error_type` 和自然语言 `error_message`，例如 `PermissionError`、`ValueError` 或 `RuntimeError`。

这种表达对人类调试够用，但对后续 retry policy、audit matrix、safety regression 和真实验证不够稳定：同一个 `PermissionError` 既可能表示 `DENY`，也可能表示 `ASK` 等待审批；同一个 `RuntimeError` 也可能是普通 runtime 失败、checkpoint 失败或 rollback 失败。

### 决策

- 在 `src/pca/tools/base.py` 中新增 `ToolErrorCode`。
- 在 `ToolResult` 中新增 `error_code: ToolErrorCode | None`。
- 成功结果必须保持 `error_code=None`。
- 失败结果必须携带 `ToolErrorCode`；旧的直接 dataclass 构造如果未传 `error_code`，默认补为 `RUNTIME_FAILED`，保持兼容。
- `ToolResult.failure(...)` 默认使用 `RUNTIME_FAILED`，调用方可显式传入更具体错误码。
- `ToolResult.from_exception(...)` 负责把当前工具链的异常映射为稳定错误码。
- 当前先覆盖 `INVALID_ARGUMENT`、`UNKNOWN_TOOL`、`PERMISSION_DENIED`、`PERMISSION_APPROVAL_REQUIRED`、`RUNTIME_FAILED`、`CHECKPOINT_FAILED`、`ROLLBACK_FAILED`。
- 从 `pca.tools` 包入口导出 `ToolErrorCode`，让它和 `ToolResult` 一样属于公开工具结果契约。

### 理由

- `ToolResult` 是工具执行结果进入 Agent Loop 和测试断言的统一信封，适合承载稳定错误语义。
- 保留 `error_type` / `error_message` 和 `ToolResult.__str__()` 可以避免破坏旧示例、旧测试和 message history 文本。
- 错误码先由当前异常和错误消息映射得到，避免在 Day 2 重写 permission、runtime、checkpoint 或 rollback 主链。
- 区分 `PERMISSION_DENIED` 和 `PERMISSION_APPROVAL_REQUIRED` 能让后续审批恢复、audit 和 safety 测试不再解析自然语言。
- 区分 checkpoint / rollback 失败，能为后续半恢复报告和审计证据留下稳定入口。

### 暂不采用

- 暂不实现 retry policy；Day 3 单独处理。
- 暂不自动接入 audit JSONL；Day 4 单独处理。
- 暂不改变 `AgentLoop` 的 tool message 文本格式。
- 暂不把所有 runtime 返回值改成 `ToolResult`。
- 暂不实现完整错误层级、用户建议字段、可恢复性枚举或 API 文档目录。

## ADR-0024：Week 5 Day 6 只在文件工具允许执行失败路径接入 FileCheckpoint rollback

日期：2026-07-02

### 背景

Week 4 已经在 shell/file 工具执行前接入 permission gate，Week 5 Day 1-Day 3 已经提供 `Workspace(root)`、`FileCheckpoint` 和 `GitCheckpoint`。但在 Day 6 之前，文件工具即使通过 permission 进入写盘路径，写盘阶段如果发生异常，也可能把半成品内容留在 workspace 内。

如果在 `DENY` 或未审批 `ASK` 阶段就创建 checkpoint，会把“尚未允许执行”的阻断路径误当成副作用路径；如果直接实现完整事务系统，又会牵涉 shell、Docker、Git、外部网络/API 和后台进程，超过 Day 6 切片。

### 决策

- 在 `src/pca/tools/file_tools.py` 中为 `WriteFileTool` 和 `EditFileTool` 增加最小 rollback 集成。
- 文件工具仍先解析 workspace 路径，再执行文件风险分类和 `PermissionPolicy.decide(...)`。
- `DecisionAction.ALLOW` 后才创建 `FileCheckpoint`，随后执行真实写盘。
- 写盘过程中抛异常时调用 `checkpoint.restore()` 恢复本地文件状态，然后继续抛出原始异常。
- `DecisionAction.ASK` 和 `DecisionAction.DENY` 在写盘前失败，不创建 checkpoint。
- rollback 失败时返回清晰 `RuntimeError`，同时包含原始写盘失败和 rollback 失败摘要。
- 示例能力边界新增 `file_tool_rollback_on_allowed_failure=True`，但保留 `rollback_auto_wired=False`，避免误解成 shell/Docker/Git 全链路 rollback。

### 理由

- permission gate 决定“是否允许进入副作用路径”，checkpoint 只服务“已经允许后的失败恢复”，两者职责不能倒置。
- `FileCheckpoint` 已经按显式文件路径保存 bytes 状态，适合文件工具的单文件写盘失败恢复。
- 继续让 `ToolRegistry` 只负责路由、结构化结果、统计和输出截断，不让它理解具体文件事务。
- 保持 `GitCheckpoint` 独立，避免 Day 6 把 tracked diff、untracked 文件、staged state 和文件工具单文件 rollback 混成一个抽象。

### 暂不采用

- 暂不把 rollback 接入 shell 命令、DockerRuntime、GitCheckpoint 或完整 AgentLoop 主链。
- 暂不实现多文件事务、后台进程清理、包安装撤销、网络/API 回滚或 workspace 外副作用恢复。
- 暂不实现交互式审批通过后的恢复执行。
- 暂不把 audit JSONL 自动接入 rollback 成功/失败事件。
- 暂不新增用户可见 undo UI 或长期 rollback 历史。

## ADR-0023：Week 5 Day 5 DockerRuntime 不可用时必须 graceful fallback

日期：2026-07-02

### 背景

Week 5 Day 4 已经定义了薄 `CommandRuntime` Protocol，并让 `ShellCommandTool` 依赖接口注入执行器。Day 5 需要把 `src/pca/runtime/docker_runtime.py` 从占位升级为最小 Docker adapter，但当前项目不能假设每台开发机都安装 Docker，也不能假设 Docker daemon 正在运行。

如果 Docker 不可用时静默回退到 `ShellRuntime`，用户会误以为命令在 sandbox 中执行，实际副作用却发生在宿主机。这个风险比直接失败更高，因为它破坏了安全边界的可解释性。

### 决策

- 新增 `DockerRuntime`，实现 `run(arguments)`，满足 `CommandRuntime` 结构化接口。
- `DockerRuntime` 复用当前命令 runtime 的输入语义：`command`、`workspace_root`、`cwd`、`timeout_seconds` 和 `env`。
- 执行前先检查 Docker CLI：`shutil.which("docker")`。
- Docker CLI 存在后再检查 daemon：`docker version --format "{{.Server.Version}}"`。
- Docker CLI 缺失时返回稳定结果：`returncode=127`、`timed_out=False`、`sandboxed=False`、`fallback="docker_unavailable"`。
- Docker daemon 不可用或检查超时时返回稳定结果：`returncode=125`、`timed_out=False`、`sandboxed=False`、`fallback="docker_unavailable"`。
- Docker 确认可用后才构造 `docker run --rm -v <workspace>:/workspace -w <cwd> <image> ...`。
- Docker 不可用时绝不回退到宿主机 shell 执行。
- `examples/04_permission_agent.py` 只声明 `docker_runtime_adapter=True`，仍保持 `sandbox=False`，避免把 adapter API 误写成完整 sandbox 能力。

### 理由

- `DockerRuntime` 是 `CommandRuntime` 的一个可替换实现，不应该改变工具层、权限层、checkpoint 层或 audit 层职责。
- graceful fallback 的核心是“清楚失败并保留结构化证据”，不是静默降级。
- `sandboxed=False` 和 `fallback="docker_unavailable"` 让调用方可以明确区分“没有执行隔离命令”和“容器内执行失败”。
- CLI 缺失和 daemon 不可用使用不同 returncode，便于后续诊断和测试。
- Day 5 先锁住不可用语义，可以让没有 Docker 的机器继续运行全量测试。

### 暂不采用

- 暂不实现完整 Docker sandbox 策略、镜像拉取策略、网络隔离、CPU/内存限制、进程树清理或容器复用。
- 暂不把 `DockerRuntime` 自动接入 `ShellCommandTool` 默认主链。
- 暂不把 Docker adapter 和 permission gate、checkpoint/rollback 或 audit 自动串联。
- 暂不承诺 Docker 能恢复网络请求、数据库写入、宿主机挂载目录之外的副作用或外部服务状态。

## ADR-0022：Week 5 Day 4 先定义薄 `CommandRuntime` Protocol

日期：2026-07-02

### 背景

Week 5 Day 1-Day 3 已经分别实现 `Workspace(root)`、`FileCheckpoint` 和 `GitCheckpoint`，但命令执行仍然由 `ShellCommandTool` 默认转发到具体 `ShellRuntime`。进入 sandbox adapter 前，系统需要先明确“命令执行器”应该暴露什么最小接口，否则 Docker runtime、fake runtime 和本地 shell runtime 会各自长出不同调用形状。

如果直接在 Day 4 实现 Docker，会把接口设计、Docker 可用性检测、容器参数、挂载目录、权限策略和 fallback 语义混在一起；如果继续让调用方类型写死为 `ShellRuntime`，后续替换 sandbox runtime 时会牵动工具层和测试。

### 决策

- 新增 `src/pca/runtime/interface.py`。
- 定义 `@runtime_checkable` 的 `CommandRuntime` Protocol。
- `CommandRuntime.run(arguments)` 接收 `dict[str, Any]` 并返回 `dict[str, Any]`。
- 返回语义继续沿用当前命令结果字段：`stdout`、`stderr`、`returncode`、`timed_out`，允许保留 `duration_ms` 等额外结构化字段。
- `ShellCommandTool` 的 runtime 注入类型从具体 `ShellRuntime | None` 改为 `CommandRuntime | None`。
- `ShellCommandTool` 默认仍使用 `ShellRuntime()`，因此现有本地命令行为不变。
- 新增 `tests/test_runtime_interface.py`，用 fake runtime 证明调用方只依赖 `run(arguments)`，不是依赖具体 `ShellRuntime`。
- 更新 `examples/04_permission_agent.py` 能力边界：`command_runtime_interface=True`，但 `sandbox=False`、`checkpoint_auto_wired=False`、`rollback_auto_wired=False`。

### 理由

- `CommandRuntime` 是执行器抽象，不是权限系统、checkpoint 系统或 audit 系统。
- Protocol 比继承基类更适合当前阶段：fake runtime、ShellRuntime 和未来 DockerRuntime 只要结构兼容即可被注入。
- 先固定薄接口，可以让 Day 5 Docker adapter 只回答“如何执行或如何清晰失败”，不把工具层、权限层和 sandbox 层搅在一起。
- fake runtime 测试能锁住替换点：`ShellCommandTool` 应调用 `runtime.run(arguments)`，而不是假设 runtime 必须是 `ShellRuntime`。
- 保持输入输出语义不变，可以避免破坏现有 `run_command`、permission gate、`ToolRegistry` 截断和示例。

### 暂不采用

- 暂不实现 Docker sandbox；Day 5 单独处理 adapter 和 Docker 不可用 fallback。
- 暂不迁移文件工具或 shell runtime 的 workspace 解析到 `Workspace(root)`。
- 暂不把 checkpoint/rollback 自动接入 runtime interface。
- 暂不把 permission gate 放进 `CommandRuntime`；权限仍在工具执行前边界处理。
- 暂不把 audit 写入、trace 透传、资源限制策略或进程树清理塞进接口本身。

## ADR-0021：Week 5 Day 3 用 git diff 实现独立 GitCheckpoint

日期：2026-07-01

### 背景

Week 5 Day 2 的 `FileCheckpoint` 已经能按显式文件列表保存和恢复 bytes 状态，但它不适合直接表达一个代码仓库的 dirty tree。Coding Agent 修改代码时，更常见的问题是“当前 git repo 中 tracked 文件相对 index 发生了哪些改动，以及能否回到某个 dirty 状态”。

如果用 `FileCheckpoint` 扫描整个仓库，会引入递归范围、性能、忽略规则和误删风险；如果提前接入完整 git workflow，又会牵涉 commit、stash、branch、merge conflict 和远程同步，超出 Day 3 切片。

### 决策

- 在 `src/pca/runtime/checkpoints.py` 中定义 `GitCheckpoint`。
- `GitCheckpoint.create(workspace)` 只接受 `Workspace`。
- 创建时先用 `git rev-parse --is-inside-work-tree` 确认 workspace 位于 git worktree 内。
- 创建时保存 `git diff --binary -- .` 的输出，表示 tracked working tree 相对 index 的 dirty diff。
- `checkpoint.restore()` 先运行 `git restore --worktree -- .`，把 tracked working tree 恢复到 index，再用 `git apply --whitespace=nowarn -` 应用保存的 diff，恢复到 checkpoint 创建时的 dirty 状态。
- 非 git workspace 抛出清晰 `ValueError`；git 命令不可用抛出清晰 `RuntimeError`；git 命令执行失败保留 stderr/stdout 摘要。
- 更新 `examples/04_permission_agent.py` 的能力边界：`git_checkpoint_api=True`，但 `checkpoint_auto_wired=False`、`rollback_auto_wired=False`。

### 理由

- git diff 是代码仓库 tracked 文件状态的天然表达，比手动递归复制更接近 Coding Agent 的真实工作流。
- `Workspace` 继续作为 root 边界输入，`GitCheckpoint` 不重新定义路径归属。
- 只处理 `tracked working tree vs index`，能把 Day 3 范围控制在 dirty diff 保存和恢复，不混入 commit/stash/branch 语义。
- restore 采用“恢复到 index，再应用 checkpoint diff”的方式，能把后续修改回滚到 checkpoint 创建时的 dirty 状态，而不是简单撤销所有改动。

### 暂不采用

- 暂不处理 untracked 文件；普通 `git diff` 不包含它们。
- 暂不保存 staged diff、commit、branch、stash 或远程状态。
- 暂不接入 `WriteFileTool`、`EditFileTool`、`ShellCommandTool` 或 permission gate 自动 rollback。
- 暂不实现事务性 restore；如果 git restore 成功但 git apply 失败，调用方会收到错误，后续需要显式半恢复报告和 audit。
- 暂不把 `GitCheckpoint` 视为 sandbox；它不能恢复网络请求、数据库写入、后台进程、包安装或 workspace 外副作用。

## ADR-0020：Week 5 Day 2 先实现独立 FileCheckpoint 文件快照 API

日期：2026-07-01

### 背景

Week 5 Day 1 已经引入 `Workspace(root)`，让 runtime 层有了统一的路径边界事实源。Day 2 需要在不扩大执行主链风险的前提下，先证明本地 workspace 文件状态可以被保存和恢复。

当前文件工具和 shell runtime 仍各自维护既有路径解析与 permission gate。直接把 rollback 接进这些主链会同时牵涉审批恢复、audit、失败语义和多文件事务，容易超过 Day 2 的教学切片。

### 决策

- 在 `src/pca/runtime/checkpoints.py` 中定义 `FileCheckpoint`。
- `FileCheckpoint.create(workspace, paths)` 只接受 `Workspace` 和显式路径列表。
- 每个路径先通过 `workspace.resolve_path(...)`，越界路径直接拒绝。
- 快照记录文件是否存在；存在时保存原始 `bytes` 内容。
- `checkpoint.restore()` 恢复快照时存在的文件内容，重建快照后被删除的文件，并删除快照时不存在但后来创建的被跟踪文件。
- 当前只支持文件粒度；如果目标是目录，则拒绝，避免误把递归目录删除纳入最小文件 checkpoint 语义。
- 更新 `examples/04_permission_agent.py` 的能力边界：`file_checkpoint_api=True`，但 `checkpoint_auto_wired=False`、`rollback_auto_wired=False`。

### 理由

- checkpoint 是“执行前状态证据”，必须复用 `Workspace` 的路径边界，不能在 checkpoint 内重复实现一套可能漂移的路径规则。
- 使用 `bytes` 保存内容可以避免当前层提前假设文本编码，适合作为最小文件状态恢复。
- 只跟踪显式传入路径，能避免 Day 2 扫描整个 workspace 或递归复制目录带来的性能和误删风险。
- 暂不自动接入 permission gate，可以保持 Week 4 shell/file gate 行为稳定，并为后续 Day 6 rollback 集成预留清晰接入点。

### 暂不采用

- 暂不实现 Git diff/stash 形式的 checkpoint；Day 3 单独处理。
- 暂不递归快照目录、权限位、mtime、符号链接元数据或文件锁状态。
- 暂不自动接入 `WriteFileTool`、`EditFileTool`、`ShellCommandTool` 或 `ShellRuntime`。
- 暂不实现失败时的事务性 restore、审计事件或用户可见 undo UI。
- 暂不宣称能恢复网络请求、数据库写入、后台进程、包安装或 workspace 外副作用。

## ADR-0019：Week 5 Day 1 先引入独立 Workspace(root) 抽象，不立即迁移主链

日期：2026-07-01

### 背景

Week 2 的文件工具和 shell runtime 已经各自实现了 `workspace_root`、相对路径解析、绝对路径越界拒绝和 `cwd` 边界。Week 4 又在这些工具执行前接入了 shell/file permission gate。

进入 Week 5 后，checkpoint、rollback 和 sandbox 都需要共享同一个“授权工作区根目录”概念。如果继续让文件工具、shell runtime、checkpoint 各自维护路径规则，后续很容易出现边界漂移：某个模块认为路径在工作区内，另一个模块却允许或拒绝不同的路径。

### 决策

- 在 `src/pca/runtime/workspace.py` 中定义 `Workspace(root)`。
- `Workspace(root)` 在构造时要求 `root` 是已存在目录，并保存解析后的绝对 `Path`。
- `Workspace.resolve_path(path)` 支持相对路径和绝对路径；相对路径基于 `root` 解析，绝对路径必须仍位于 `root` 内。
- `Workspace.resolve_path(path)` 拒绝空路径、非字符串/PathLike 路径、绝对路径越界和 `..` 解析后越界。
- `Workspace.contains(path)` 返回布尔值，用于后续 checkpoint/sandbox 判断路径归属；越界或非法路径返回 `False`。
- 本次只新增独立抽象和 `tests/test_workspace.py`，不立即替换 `file_tools.py` 或 `shell_runtime.py` 的既有主链。

### 理由

- Workspace 是“路径边界事实源”，permission 是“是否允许本次操作”的策略层；两者职责不同，不能混在一起。
- 先独立实现并测试 `Workspace(root)`，可以为 Day 2 checkpoint、Day 3 git checkpoint 和 Day 4 runtime interface 复用同一个边界对象。
- 不立即迁移主链可以避免破坏 Week 4 已经通过的 shell/file permission gate，也让 Day 1 的行为变化保持最小。
- `contains(...)` 不抛越界异常，更适合后续做预检、过滤和报告；`resolve_path(...)` 则适合需要拿到真实路径并执行文件操作的边界。

### 暂不采用

- 暂不实现 checkpoint、rollback 或 Docker sandbox。
- 暂不把 `Workspace` 接入 `ReadFileTool`、`WriteFileTool`、`EditFileTool` 或 `ShellRuntime`。
- 暂不支持多个 workspace、workspace trust level、只读 workspace 或路径级权限。
- 暂不把 symlink 策略扩展成独立配置；当前使用 `Path.resolve()` 后再做 root 归属判断。

## ADR-0018：Week 4 Day 6 先实现独立权限审计事件和 JSONL 写入

日期：2026-06-22

### 背景

Week 4 Day 1-Day 5 已经让 Permission System 具备风险分类、策略判断、审批对象、shell gate 和文件写盘前风险 gate。当前系统能阻止 `DENY` 和未审批的 `ASK` 操作静默执行，但缺少稳定的事实记录：事后很难回答“哪个工具、哪条规则、哪个策略动作、是否执行”。

如果直接把审计逻辑硬接入 shell/file gate，很容易把“记录事实”和“改变行为”混在一起，也会在审批恢复、checkpoint、rollback 尚未完成前扩大主链改动范围。

### 决策

- 新增 `src/pca/permissions/audit.py`。
- 定义 `PermissionAuditEvent`，保存 `timestamp`、`tool_name`、`action`、`risk_level`、`matched_rule`、`reason` 和 `executed`。
- `PermissionAuditEvent.to_dict()` 将 `datetime` 和 `DecisionAction` 转成稳定 JSON 字段。
- 定义 `append_audit_event(path, event)`，把单个事件追加为一行 JSONL。
- 新增 `tests/test_permissions_audit.py` 覆盖字段保存、稳定序列化和 JSONL 追加写入。
- 本次不把 audit 自动接入 `ShellCommandTool`、`WriteFileTool` 或 `EditFileTool`，避免 Day 6 改变现有 allow / ask / deny 行为。

### 理由

- audit 是事实记录层，不是策略层；它应该记录发生了什么，而不是决定能不能执行。
- JSONL 一行一个事件，适合后续追加、回放、安全回归矩阵和真实验证报告。
- `executed` 字段能区分“被允许且执行过”和“因为 ASK/DENY 没有执行”，为后续审批恢复和 rollback 留证据。
- 先独立实现数据结构和持久化函数，可以让 Week 4 Day 7 示例和 Week 6 audit 完整性检查复用同一 API。

### 暂不采用

- 暂不实现交互式审批 UI。
- 暂不让 `ASK` 审批后自动恢复执行。
- 暂不做 checkpoint、rollback 或 sandbox 集成。
- 暂不自动透传 `TraceContext`。
- 暂不记录完整命令输出、文件内容、secret 或 env 值。

## ADR-0017：Week 4 Day 5 在文件工具写盘前接入文件风险 gate

日期：2026-06-22

### 背景

Week 4 Day 4 已经让 `run_command` 在进入 `ShellRuntime` 前经过 `classify_command(...)` 和 `PermissionPolicy.decide(...)`。但文件工具仍然只依赖 `workspace_root` 边界：路径在工作区内就可以直接写盘。

这会留下一个重要缺口：覆盖已有文件、删除式编辑或大范围替换即使发生在工作区内，也可能破坏用户代码。workspace 边界只能回答“能不能碰这个路径”，不能回答“这次修改是否需要用户确认”。

### 决策

- 新增 `src/pca/permissions/file_risk.py`。
- 定义 `classify_file_change(...)`，返回现有 `RiskAssessment`。
- `write_file` 写新文件分类为 `RiskLevel.SAFE`，覆盖已有文件分类为 `RiskLevel.ASK`。
- `edit_file` 小范围精确替换分类为 `RiskLevel.SAFE`。
- `edit_file` 空字符串替换或大范围缩减分类为 `RiskLevel.ASK`。
- 在 `WriteFileTool._run(...)` 和 `EditFileTool._run(...)` 写盘前调用文件风险分类和 `PermissionPolicy.decide(...)`。
- `DecisionAction.ALLOW` 继续原写盘路径。
- `DecisionAction.ASK` 抛出 `PermissionError`，由 `ToolRegistry.run(...)` 转成失败 `ToolResult`，表示需要审批但不执行。
- 本次不实现 audit JSONL、checkpoint、rollback、完整 diff UI 或审批通过后的恢复执行。

### 理由

- 文件风险分类属于 permission 模块，可以和 shell 风险共用 `RiskAssessment` / `PermissionPolicy` 模型。
- 文件工具最接近真实写盘动作，把 gate 放在 `WriteFileTool` / `EditFileTool` 写盘前能证明 ASK 不会修改磁盘。
- `ToolRegistry` 继续保持通用路由、结果包装、统计和截断职责，不需要理解文件覆盖或删除式编辑语义。
- `_resolve_workspace_path(...)` 继续负责 workspace 边界，不和 permission gate 混在一起。
- 没有交互式审批 UI 前，`ASK` 必须失败返回，不能被当成允许执行。

### 暂不采用

- 暂不生成文件 diff 或完整审批 UI。
- 暂不把审批对象接回 `write_file` / `edit_file` 的恢复执行链。
- 暂不把文件风险写入 JSONL audit；Day 6 统一处理审计事件。
- 暂不实现 checkpoint / rollback；后续 Git Safety 和 workspace checkpoint 再设计。
- 暂不把所有文件编辑都默认 ASK；当前只拦截覆盖和删除式风险，保留新文件写入与小范围替换的学习闭环。

## ADR-0016：Week 4 Day 4 在 ShellCommandTool 执行前接入 shell gate

日期：2026-06-22

### 背景

Week 4 Day 1-Day 3 已经分别实现了命令风险分类、权限策略判断和审批对象。此前这些对象仍未接入 `run_command` 主链，`ShellCommandTool` 会把命令直接转发给 `ShellRuntime.run(...)`，导致 `RiskAssessment` 和 `PermissionDecision` 只能被单元测试证明，不能阻止真实 shell 执行。

Day 4 的目标是证明危险命令不会进入真实 runtime，`ASK` 命令不会在没有用户确认时静默执行，同时保持安全命令的原执行路径。

### 决策

- 将 shell gate 放在 `src/pca/tools/shell_tools.py` 的 `ShellCommandTool._run(...)`。
- `ShellCommandTool._run(...)` 先调用 `classify_command(arguments["command"])`。
- 再调用 `PermissionPolicy.decide(assessment)`。
- `DecisionAction.ALLOW` 时继续调用 `self._runtime.run(arguments)`。
- `DecisionAction.ASK` 时抛出 `PermissionError`，由 `ToolRegistry.run(...)` 转成失败 `ToolResult`，表示需要审批但不执行。
- `DecisionAction.DENY` 时抛出 `PermissionError`，由 `ToolRegistry.run(...)` 转成失败 `ToolResult`，并保证不进入 runtime。
- 向后兼容函数 `pca.tools.shell_tools.run_command(...)` 也改为通过 `ShellCommandTool().run(arguments)`，避免绕过 gate。
- 本次不实现交互式审批 UI、审批通过后恢复执行、audit JSONL、文件风险分类或 sandbox。

### 理由

- `ShellCommandTool` 是 `run_command` 的工具语义边界，能在具体工具执行前拦截，同时保留 `ShellRuntime` 作为纯执行器。
- `ShellRuntime` 继续负责 workspace、cwd、timeout、env 和输出脱敏等底层安全边界，不混入业务权限策略。
- `ToolRegistry` 继续负责路由、结果包装、统计和截断，不需要理解 shell 命令风险。
- `ASK` 在没有审批 UI 时必须失败返回，不能把“需要问用户”误当成“允许执行”。
- fake runtime 测试能证明拦截发生在执行前，而不是执行后包装错误。

### 暂不采用

- 暂不把审批通过结果接回执行链；后续需要 CLI/UI 和 audit 一起设计。
- 暂不把权限结果写入 `ToolResult` 的专门字段；当前先用失败 `ToolResult` 表达阻断。
- 暂不在 `ShellRuntime` 中重复分类命令；runtime 仍保持执行器职责。
- 暂不阻止所有可能危险的 shell 形式；当前分类器仍是最小启发式规则，后续通过文件风险、audit、真实验证和 sandbox 加固。

## ADR-0015：Week 4 Day 3 用独立审批对象承接 ASK 策略结果

日期：2026-06-22

### 背景

Week 4 Day 1 已经能把命令分类为 `RiskAssessment`，Day 2 已经能把风险映射为 `PermissionDecision(action=ALLOW/ASK/DENY)`。其中 `DecisionAction.ASK` 只表示策略要求人工确认，还不是“用户已经同意执行”。

如果后续 shell gate 直接把 `ASK` 当成布尔值处理，就会丢失请求 id、工具名、命令摘要、过期时间和用户理由，也无法为 audit 留下稳定证据。

### 决策

- 在 `src/pca/permissions/approval.py` 定义 `ApprovalRequest`。
- `ApprovalRequest` 保存 `request_id`、`tool_name`、`command_summary`、`PermissionDecision`、`created_at` 和 `expires_at`。
- `ApprovalRequest.is_expired(now)` 负责判断请求是否过期。
- 定义 `ApprovalDecision`，保存 `request_id`、`approved`、`user_reason` 和 `decided_at`。
- 提供 `ApprovalDecision.approve(...)` 和 `ApprovalDecision.reject(...)` 两个工厂方法。
- 拒绝空 `request_id`、空 `tool_name`、空 `command_summary`、非 `PermissionDecision` 和无效过期时间。
- 本次不修改 `ShellRuntime`、`ShellCommandTool`、`ToolRegistry`、`AgentLoop` 或 audit。

### 理由

- `PermissionDecision` 是系统策略，`ApprovalDecision` 是用户决定；二者分离后才能清楚表达“系统要求问”和“用户回答了什么”。
- `ApprovalRequest` 保留原始策略判断，后续审批 UI 和审计事件可以解释为什么需要审批。
- `request_id` 能把请求、用户决定和未来 audit 关联起来。
- `expires_at` 避免用户很久以后批准一个已经不再对应当前上下文的危险操作。
- 先让审批对象纯数据化，可以在 Day 4 接 shell gate 前稳定 API 和测试。

### 暂不采用

- 暂不生成默认 request id 或默认过期时间；当前由调用方显式传入，便于测试和后续 gate 控制。
- 暂不让 `ApprovalDecision` 自动执行命令。
- 暂不把审批结果写入 JSONL audit。
- 暂不把过期请求接入 `ShellRuntime` 或 `ShellCommandTool`；shell gate 留到 Day 4。
- 暂不实现交互式 CLI prompt、Web UI 或长期审批存储。

## ADR-0014：Week 4 Day 2 用独立策略层映射风险到权限动作

日期：2026-06-21

### 背景

Week 4 Day 1 已经实现 `RiskLevel`、`RiskAssessment` 和 `classify_command(...)`。风险分类只能回答“命令看起来多危险”，还不能回答“本次工具调用应该允许、询问还是拒绝”。如果把这两个概念混成一个枚举，后续就很难支持按用户配置、workspace 信任级别、工具类型或审批状态改变策略结果。

同时，当前权限系统仍未接入 shell 执行链。如果 Day 2 同时修改 `ShellRuntime` 或 `ToolRegistry`，策略对象还没稳定就会影响已有工具主链。

### 决策

- 在 `src/pca/permissions/policy.py` 定义 `DecisionAction`：`ALLOW`、`ASK`、`DENY`。
- 定义 `PermissionDecision(action, reason, assessment)`，保留原始 `RiskAssessment` 作为决策证据。
- 实现 `PermissionPolicy.decide(assessment)`。
- 默认策略映射为：`RiskLevel.SAFE -> ALLOW`、`RiskLevel.ASK -> ASK`、`RiskLevel.DENY -> DENY`。
- `PermissionPolicy.decide(...)` 只接受 `RiskAssessment`，拒绝原始命令字符串或任意对象。
- 本次不修改 `ShellRuntime`、`ShellCommandTool`、`ToolRegistry`、`AgentLoop`、审批对象或 audit。

### 理由

- `RiskLevel` 是事实判断，`DecisionAction` 是策略判断；分离后才能支持未来可配置策略。
- `PermissionDecision` 保留 `assessment`，可以让后续审批 UI 和审计日志看到“为什么做出这个动作”。
- policy 层保持纯判断，不执行命令、不做人机交互、不写审计，便于单元测试和后续替换。
- 先稳定 `PermissionPolicy` API，再在 Day 3-Day 4 接入审批对象和 shell gate，能降低主链回归风险。

### 暂不采用

- 暂不实现用户配置、workspace trust、工具 allowlist 或 denylist。
- 暂不实现审批请求、审批过期或审批结果对象。
- 暂不把 `PermissionDecision` 写入 JSONL audit。
- 暂不阻止 `run_command` 执行危险命令；shell gate 留到 Day 4。
- 暂不引入 Open Policy Agent 或第三方策略引擎。

## ADR-0013：Week 4 Day 1 先实现独立风险分类器，不接入执行链

日期：2026-06-21

### 背景

Week 4 开始建设 Permission System。当前 `ShellRuntime.run(...)` 会在工作区边界和 timeout 校验后直接执行命令，`ShellCommandTool` 只负责把工具调用转发给 runtime，`ToolRegistry` 只负责工具路由、结果包装、输出截断和 stats。

如果第一天就把权限逻辑硬接进 shell runtime 或 registry，分类 API、策略判断和审批对象还没稳定，就会影响已有 Agent Loop 与 Tool Runtime 行为。更稳妥的顺序是先定义可测试的风险分类结果，再由后续 Day 2-Day 4 接入策略和执行前 gate。

### 决策

- 在 `src/pca/permissions/risk.py` 定义 `RiskLevel`：`SAFE`、`ASK`、`DENY`。
- 定义 `RiskAssessment(level, reason, matched_rule)`，让分类结果可测试、可解释。
- 实现 `classify_command(command)`，支持字符串命令和 `list[str]` 命令。
- 规则顺序为：先匹配明显破坏性 `DENY`，再匹配联网、内联代码、shell 操作符等 `ASK`，最后默认 `SAFE`。
- 本次不修改 `ShellRuntime`、`ShellCommandTool`、`ToolRegistry` 或 `AgentLoop`。

### 理由

- 分类是策略判断和审批流的输入，不应该和执行拦截混在同一天完成。
- `RiskAssessment.reason` 和 `matched_rule` 能让后续审批 UI、审计日志和测试知道为什么做出分类。
- 独立纯函数更容易用 TDD 覆盖，也不会破坏现有 117 个测试和示例。
- 先保留启发式字符串规则，明确误判边界，后续再通过 policy、audit 和真实验证加固。

### 暂不采用

- 暂不实现 `PermissionPolicy.decide(...)`。
- 暂不实现审批对象、审批过期、审计 JSONL。
- 暂不阻止 `run_command` 执行危险命令；shell gate 留到 Day 4。
- 暂不实现完整 shell AST、跨平台解析器、命令 allowlist 或 sandbox。

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
