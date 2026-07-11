# 代码完成度审计（2026-07-10）

## 1. 报告性质与审计口径

- **审计日期**：2026-07-10。
- **报告性质**：基于当日源码、`PROJECT_REQUIREMENTS.md`、`docs/INDUSTRIAL_STANDARDS.md`、`docs/17_WEEK6_HARDENING_REPORT.md` 和已取得只读证据形成的静态快照；本报告不是实时状态源，后续进度以 `docs/09_NEXT_ACTIONS.md` 为准。
- **只读边界**：本报告只建议、**不修改代码**，不修改测试，也不推进 Week 7 Day 1；所有整改均为“**等待用户批准**”。
- **当日验证证据**：全量测试为 `206 passed, 1 skipped`，5 个示例通过，`python -m compileall src examples -q` 通过且无输出。
- **阶段结论**：上述证据符合 Week 6 “带边界放行”以及进入 Week 7 学习切片的预期，但不符合最终工业级产品验收。Week 6 放行只表示当前课程切片在已声明边界内可继续学习，不表示 24 周最终产品完成。

本审计不执行破坏性命令。包装命令问题采用源码静态分类推导；`ToolRegistry` 与审批对象问题采用任务已取得的只读构造证据并与当前源码逐行核对。本轮尝试运行纯分类/构造探针时被执行环境审批额度限制拦截，因此未把该次尝试写成成功运行证据。

## 2. 三种“完成”的严格区分

| 层级 | 含义 | 本次结论 |
|---|---|---|
| 测试通过 | 现有测试集在指定环境和范围内没有发现回归 | 当日有 `206 passed, 1 skipped`、5 个示例和 compileall 证据；只能证明现有覆盖范围 |
| 课程阶段完成 | 当前学习切片的目标、测试、示例和已声明边界足以进入下一学习切片 | Week 6 可带边界放行；Week 7 Day 1 尚未由本报告启动 |
| 最终工业级完成 | 满足 `PROJECT_REQUIREMENTS.md` 最终验收和工业标准，包括安全、稳定错误、完整生命周期、质量门禁、真实 E2E 等 | **未完成**；P0/P1 缺口仍在，不能以测试绿灯替代产品验收 |

## 3. 发现总览

| 编号 | 优先级 | 模块 | 简述 | 批准状态 |
|---|---|---|---|---|
| F-01 | P0 | permissions / tools | shell 包装命令可绕过真实子命令风险分类 | 等待用户批准 |
| F-02 | P1 | tools | 非字符串且不可哈希工具名破坏稳定 `ToolResult` 信封 | 等待用户批准 |
| F-03 | P1 | permissions | 审批对象对错误类型产生不稳定异常语义 | 等待用户批准 |
| F-04 | P1 | permissions / observability | audit 的 `executed` 不是最终执行成功事实 | 等待用户批准 |
| F-05 | P1 | engineering | 缺少 lint、type-check 和 CI 质量门禁 | 等待用户批准 |
| F-06 | P1 | tools / runtime | Workspace 路径边界逻辑重复 | 等待用户批准 |
| F-07 | P1 | tools / permissions | retry 仅判断、不自动执行；审批不能恢复 | 等待用户批准 |
| F-08 | P1 | runtime | rollback 仅覆盖局部文件失败，未覆盖跨副作用事务 | 等待用户批准 |

## 4. 详细发现

### F-01：包装命令绕过 shell 分类

- **优先级**：P0。
- **模块**：`src/pca/permissions/risk.py`、`src/pca/tools/shell_tools.py`。
- **证据**：`classify_command(...)` 规范化后只把 `lowered_parts[0]` 当作可执行程序；deny 规则只识别首 token 为 `rm`、`rmdir`、`del`、`erase`、`remove-item` 或 `format`。因此对无副作用的分类输入 `cmd /c del /s /q harmless-target`，首 token 为 `cmd`；对 `powershell -Command Remove-Item harmless-target -Recurse -Force`，首 token 为 `powershell`。当前规则既不展开 wrapper，也没有 wrapper 专用 ASK 规则，两者可能落入 `SAFE/default_safe`。这是静态分类证据，未执行其中的子命令。
- **差距**：分类器判断的是包装器，而不是实际待执行子命令，无法满足“默认拒绝高风险操作”和所有 shell 操作有可靠策略边界的最终要求。
- **影响**：攻击者或错误调用可以把删除、网络、内联代码等高风险动作藏在 `cmd /c`、`powershell -Command` 等包装层中，使 permission gate 在执行前错误放行。
- **建议**：优先实现受支持 wrapper 的结构化展开并递归分类；无法可靠解析、嵌套层数超限、引号不平衡或遇到未知 wrapper 时默认 `ASK`，不得默认 `SAFE`。需新增 classification tests 和 safety tests，至少覆盖字符串/数组形式、大小写、完整可执行路径、嵌套 wrapper、引号、shell operator、危险子命令和未知 wrapper 的 fail-closed 行为。测试只调用分类器或 fake runtime，不执行破坏性命令。
- **批准状态**：**等待用户批准**后修改代码和测试。

### F-02：`ToolRegistry.run` 可能逃逸稳定结果信封

- **优先级**：P1。
- **模块**：`src/pca/tools/registry.py`。
- **证据**：已取得的只读构造证据为 `ToolRegistry.run([], {})` 在失败统计阶段产生 `TypeError: unhashable type: 'list'`。当前源码先在 `get(name)` 中产生参数错误并构造失败 `ToolResult`，随后 `_record_stats(name=name, ...)` 对 `_stats.setdefault(name, ...)` 使用未校验、不可哈希的 list，再次抛错。
- **差距**：`run(...)` 声明返回稳定 `ToolResult`，但失败记录本身可抛出第二个异常，错误信封不能覆盖坏工具名输入。
- **影响**：AgentLoop 可能收到注册表异常而不是带 `INVALID_ARGUMENT` 的结果；统计、错误分类、retry 和审计看到的语义不一致。
- **建议**：在计时/执行前验证并规范化工具名，或以稳定占位键记录无效调用；确保错误构造和统计路径不会被原始坏输入再次破坏。新增 list、dict、空值、空白字符串和未知合法字符串的回归测试，并断言返回 `ToolResult`、错误码及 stats 行为。
- **批准状态**：**等待用户批准**后修改代码和测试。

### F-03：审批对象错误语义不稳定

- **优先级**：P1。
- **模块**：`src/pca/permissions/approval.py`。
- **证据**：已取得的只读构造证据为 `ApprovalDecision(request_id=1, ...)` 产生 `AttributeError`。当前 `ApprovalDecision.__post_init__` 直接调用 `self.request_id.strip()`；`ApprovalRequest` 的 `request_id`、`tool_name`、`command_summary` 也采用相同模式。
- **差距**：公开数据对象没有先做类型判断，坏输入泄漏实现细节异常，未形成可预测的 `TypeError`/`ValueError` 契约。
- **影响**：API 调用方、审计层和未来 approval resume 无法稳定区分参数错误与内部故障，错误码映射也可能错误地归入 runtime failure。
- **建议**：所有审批字符串字段先验证类型，再验证非空；同时验证 `approved` 必须为 bool、时间字段为可比较且时区语义明确。新增构造器、`approve(...)`、`reject(...)` 与过期判断的类型/边界测试。
- **批准状态**：**等待用户批准**后修改代码和测试。

### F-04：audit `executed` 混淆授权与执行结果

- **优先级**：P1。
- **模块**：`src/pca/permissions/audit.py`、`src/pca/tools/shell_tools.py`、`src/pca/tools/file_tools.py`。
- **证据**：shell/file gate 在真实 runtime 或文件写入之前调用 `record_permission_decision(..., executed=decision.action is ALLOW)`；事件随后立即落盘。因此 `executed=true` 只表示 ALLOW 已获准进入后续路径，不表示 runtime 已开始，更不表示最终成功。
- **差距**：单一布尔字段无法表达 authorized、started、succeeded、failed、rolled_back 等生命周期状态，也没有后置结果事件与同一调用关联。
- **影响**：事故回放、成功率、合规审计和 rollback 分析可能把执行失败误记为成功执行。
- **建议**：用明确生命周期字段区分 `authorized`、`started`、`succeeded`，或保留 permission decision event 并新增关联 tool result event；事件需共享 `trace_id`、`tool_call_id`/operation id。新增允许后 runtime 失败、audit 写入失败、permission 拒绝、写盘失败并 rollback 的顺序与关联测试。
- **批准状态**：**等待用户批准**后修改代码和测试。

### F-05：缺少 lint、type-check 和 CI 配置

- **优先级**：P1。
- **模块**：项目级工程质量。
- **证据**：根 `pyproject.toml` 只有 project 和 pytest 配置；仓库没有 `.github/workflows/` 质量工作流，也未发现 Ruff、mypy、Pyright、Flake8 或 Pylint 的项目配置。现有 `206 passed, 1 skipped` 不能替代 lint/type-check/CI 证据。
- **差距**：不满足 `PROJECT_REQUIREMENTS.md` 对类型检查、lint、格式检查和 CI 的最终要求，也不具备在干净环境自动复现质量门禁的证据。
- **影响**：类型错误、未使用代码、格式漂移和环境差异可能在本地 pytest 之外进入主线；作品集无法展示持续验证能力。
- **建议**：明确 Python 版本矩阵和最小门禁，选择并锁定 lint/format/type 工具，先建立本地命令，再接入 CI；记录基线债务，不用大范围静默自动修复掩盖现状。
- **批准状态**：**等待用户批准**后增加配置、依赖和 CI。

### F-06：Workspace 路径逻辑重复

- **优先级**：P1。
- **模块**：`src/pca/tools/file_tools.py`、`src/pca/runtime/workspace.py`、`src/pca/runtime/shell_runtime.py`。
- **证据**：`Workspace(root)` 已提供根目录验证、`resolve_path(...)` 和 `contains(...)`；文件工具仍保留 `_resolve_workspace_root(...)`、`_resolve_workspace_path(...)`，shell runtime 也维护独立 cwd/workspace 校验。
- **差距**：授权工作区还不是所有运行时和工具的唯一事实源。
- **影响**：三套解析逻辑可能在 symlink、相对路径、非字符串 path、缺失目录和平台差异上漂移，形成边界不一致。
- **建议**：先定义统一 `Workspace` 输入契约和兼容迁移顺序，再让 file/shell/checkpoint 复用；迁移前建立等价性与 Windows 边界回归测试，避免一次性重构改变安全语义。
- **批准状态**：**等待用户批准**后修改代码和测试。

### F-07：retry 与 approval 尚未闭环

- **优先级**：P1。
- **模块**：`src/pca/tools/retry.py`、`src/pca/permissions/approval.py`、AgentLoop 工具调用链。
- **证据**：`RetryPolicy.decide(...)` 和 `should_retry(...)` 只返回是否可重试，不重新调度工具；ASK 当前抛出 `PermissionError`，审批对象未与暂停调用、用户决定和恢复执行关联。
- **差距**：缺少次数上限、退避、幂等性/副作用判断、取消与 trace 关联；缺少可持久化 pending request 及批准后仅恢复原调用一次的协议。
- **影响**：临时 runtime failure 仍依赖 LLM 自行决定；审批通过也无法安全恢复，未来简单自动重试还可能重复副作用。
- **建议**：按路线分阶段实现：先定义 retry orchestration 状态机与幂等边界，再接 AgentLoop；approval resume 必须绑定原请求、参数摘要、过期时间和一次性消费。为批准、拒绝、过期、重复决定、恢复失败和非幂等工具建立集成测试。
- **批准状态**：**等待用户批准**后修改代码和测试。

### F-08：rollback 未覆盖跨副作用事务

- **优先级**：P1。
- **模块**：`src/pca/runtime/checkpoints.py`、file/shell/git/runtime 主链。
- **证据**：文件工具在单次写盘异常时使用 `FileCheckpoint` 恢复显式文件；`GitCheckpoint` 是独立 API，shell、Docker、Git、网络等副作用未自动接入统一事务；untracked/staged 和多操作链也不是完整恢复协议。
- **差距**：当前 rollback 是局部补偿，不是跨工具、跨副作用的原子事务或可靠 saga。
- **影响**：多步骤任务在中途失败时可能留下部分文件、Git 状态或外部副作用；把“局部恢复成功”宣传为完整 rollback 会高估安全能力。
- **建议**：先定义 operation lifecycle、可补偿副作用清单和不可逆操作的默认 ASK/DENY；再按文件、Git、sandbox、网络逐类实现补偿与失败语义。增加跨步骤失败、补偿失败和部分恢复的 E2E 证据。
- **批准状态**：**等待用户批准**后修改代码和测试。

## 5. 模块完成度矩阵

| 模块 | 当前状态 | 主链证据 | 测试证据 | 符合当前阶段 | 距离最终目标 |
|---|---|---|---|---|---|
| core | 已实现当前阶段 | `AgentLoop`、`Message`、`ToolCall`、`ScriptedLLM`、run 级 `trace_id` 与工具结果回写已形成最小闭环 | 包含在当日全量 `206 passed, 1 skipped`；5 个示例覆盖最小 Agent/tool 路径 | 是，可支持 Week 6 带边界放行 | 缺真实 LLM adapter、自动恢复编排、完整结构化 trace/replay 和最终 E2E |
| tools | 已实现基础/编排部分 | `Tool`、schema、`ToolRegistry`、文件/shell 工具、错误码、输出截断、stats、retry policy 候选已存在 | 工具、shell、安全与 E2E 测试包含在当日全量证据中 | 是，但必须保留已声明边界 | wrapper P0、稳定坏输入、自动 retry、更多工具、统一 workspace 与完整质量证据未完成 |
| permissions | 部分实现 | 风险分类、policy、approval 数据对象、shell/file gate、摘要 audit 已接入或已提供 | permission/safety 回归包含在当日全量证据中 | 部分符合；足以教学验证，不足以最终验收 | wrapper 绕过、approval resume、稳定校验、完整 audit 生命周期、默认 fail-closed 扩展仍缺失 |
| runtime | 部分实现 | `ShellRuntime`、`CommandRuntime`、`Workspace`、`FileCheckpoint`、`GitCheckpoint`、`DockerRuntime` 与局部文件 rollback 已存在 | shell、workspace、checkpoint/rollback 与示例证据包含在当日验证中 | 部分符合；当前局部能力可用 | 统一 Workspace、默认隔离、跨副作用 rollback、资源/性能证据与生产级 sandbox 未完成 |

## 6. 纯占位模块：只列路线缺口

以下目录当前仅作为未来路线入口，不纳入本次模块流程验收，也不能画成已接入主链：

- `src/pca/context`：Repo Scanner/Repo Map、检索、压缩和 prompt builder 尚待后续学习切片实现。
- `src/pca/memory`：长期记忆、任务记忆、SQLite/vector/graph 后端尚未实现。
- `src/pca/mcp`：client/server 尚未实现。
- `src/pca/observability`：结构化日志、tracing 查询和 replay 尚未实现。
- 根 `src/pca/cli.py` 等尚未形成最终产品 CLI 主链。

这些占位目录是路线缺口，不因文件存在而算“模块已完成”，也不纳入 core/tools/permissions/runtime 的当前阶段通过率。

## 7. 建议整改顺序

| 顺序 | 整改项 | 目标证据 | 批准状态 |
|---|---|---|---|
| 1 | P0 wrapper 分类与 safety tests | wrapper 展开/默认 ASK；分类器与 fake runtime 安全回归，不执行破坏性命令 | 等待用户批准后修改代码 |
| 2 | `ToolRegistry` / approval 稳定错误 | 所有坏输入返回或抛出约定错误，注册表不逃逸 `ToolResult` | 等待用户批准后修改代码 |
| 3 | audit 生命周期 | authorized/started/succeeded/failed/rolled_back 可关联、可回放 | 等待用户批准后修改代码 |
| 4 | lint / type-check / CI | 本地命令与干净 CI 环境均可复现并通过 | 等待用户批准后增加配置 |
| 5 | 按路线实现 retry / approval / runtime 隔离 | 有界 retry、审批恢复、统一 Workspace、sandbox 与跨副作用补偿的集成/E2E 证据 | 等待用户批准后修改代码 |

## 8. 最终结论

2026-07-10 的 `206 passed, 1 skipped`、5 个示例和 compileall 证明当前教学主链在现有覆盖范围内稳定，并支持 Week 6 带边界放行；它们不证明最终工业级产品完成。当前最先需要处理的是 P0 包装命令分类漏洞，其后是 `ToolRegistry`/approval 稳定错误、audit 生命周期和工程质量门禁。本文只给出审计建议，**不修改代码**；全部整改均**等待用户批准**，本报告不推进 Week 7 Day 1。
