# 24 Week Industrial Learning and Build Plan

## 总原则

- 周期：24 周。
- 节奏：2 周能力实现 + 1 周工业级加固为主，关键阶段插入真实验证。
- 每周必须产出可运行、可测试、可验收成果。
- 每日任务必须绑定代码、测试、文档、复盘和验收，不写空泛“学习某框架”。
- 每一阶段都要更新 `docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md`，涉及架构取舍时更新 `docs/06_ARCHITECTURE_DECISIONS.md`。

## 阶段总览

| 阶段 | 周次 | 主题 | 可运行成果 |
|---|---:|---|---|
| A | 1-3 | Agent Core + Tool Runtime 基线与加固 | mock LLM coding harness、文件工具、shell runtime、结构化结果、初步 observability |
| B | 4-6 | Permission + Sandbox + Git Safety | 危险命令分类、审批、审计、checkpoint、git diff/rollback |
| C | 7-10 | Coding Agent | repo map、symbol index、patch/diff、test/lint/type/git workflow |
| D | 11-14 | Retrieval / RAG | document loader、chunking、BM25/vector、rerank、citation、RAG eval |
| E | 15-18 | Personal Assistant Memory | preference/project/task/learning memory、context compression、personal state graph |
| F | 19-20 | Planner / State Machine / Events | planner/executor/reviewer、state graph、interrupt、replay |
| G | 21-22 | Evaluation / Observability / CI | golden/regression/safety/e2e/eval harness、trace dashboard files、CI |
| H | 23-24 | Productization / Portfolio | CLI、真实场景验证、release checklist、作品集文档 |

## Week 1 - Agent Core 基线

已完成，保留为历史基线。

1. 本周主题：Agent loop、message history、mock LLM、tool result injection。
2. 工业级目标：建立可测试的最小闭环。
3. 核心概念：ReAct、Message、ToolCall、max_turns、trajectory。
4. 参考项目：mini-SWE-agent 的线性 history 和最小 loop。
5. 代码模块：`src/pca/core/messages.py`、`mock_llm.py`、`agent_loop.py`。
6. 测试：`tests/test_agent_loop.py`、示例回归。
7. 文档：README、ADR、学习笔记、面试题。
8. 验收：`python examples/01_minimal_agent.py` 输出完整链路。
9. 风险：mock LLM 被误认为真实模型能力。
10. 新增能力：Agent 能循环调用工具并返回最终回答。

| Day | 今日学习目标 | 今日代码任务 | 今日阅读任务 | 今日测试任务 | 今日文档任务 | 今日复盘问题 | 今日完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 理解 `Message`/`ToolCall` | 实现 `src/pca/core/messages.py` | mini-SWE-agent agent class | 新增消息结构测试 | 记录 Agent Loop 直觉 | 为什么 tool result 要进 history | message 测试通过 |
| 2 | 理解 mock LLM | 实现 `ScriptedLLM.complete` | ReAct method | mock response 测试 | 记录 mock 价值 | 为什么不用真实 API | mock 测试通过 |
| 3 | 理解 loop stop | 实现 `AgentLoop.run` | mini-SWE trajectory | tool_call 闭环测试 | 画 loop Mermaid | 什么时候停止 | loop 测试通过 |
| 4 | 理解工具失败 | 错误写回 history | OpenAI tool result 概念 | unknown tool 测试 | 记录失败路径 | 崩溃和恢复区别 | 失败测试通过 |
| 5 | 理解示例入口 | 更新 `examples/01_minimal_agent.py` | README 示例写法 | 子进程示例测试 | README 最小运行 | 示例为何要测试 | 示例可运行 |
| 6 | 文档表达 | 无生产代码 | README 结构 | 全量测试 | Week 1 讲解稿 | 面试如何讲 | 文档和测试通过 |
| 7 | 复盘加固 | 小边界修复 | pytest docs | 全量回归 | 面试题归档 | 还缺什么工业级能力 | 无阻塞进入 Week 2 |

## Week 2 - Tool Runtime 基线

已完成，保留为历史基线。

1. 主题：Tool interface、registry、schema、file tools、shell runtime、ToolResult。
2. 工业级目标：让工具调用具备契约、边界和结构化结果。
3. 概念：ToolParameter、ToolRegistry、workspace_root、timeout、ToolResult。
4. 参考项目：mini-SWE-agent runtime；LangChain tools；OpenAI tool calling。
5. 代码：`src/pca/tools/*`、`src/pca/runtime/shell_runtime.py`。
6. 测试：工具 schema、文件边界、shell timeout、env 脱敏。
7. 文档：ADR-0003/0004/0006/0007、Week 2 面试稿。
8. 验收：当时基线测试和两个示例通过，具体最新数字以 `docs/09_NEXT_ACTIONS.md` 为准。
9. 风险：把 ToolResult 误当权限系统。
10. 新增能力：Agent 能读写编辑文件、执行受限命令、结构化回写结果。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 工具 schema | `ToolParameter`、`Tool.to_schema` | JSON Schema object | schema/required/type 测试 | ADR-0006 | schema 能替代安全校验吗 | schema 测试通过 |
| 2 | 默认工具 schema | `examples/02_tool_agent.py` | OpenAI/Anthropic tools | 示例 JSON 测试 | 资源库 | adapter 应从哪拿工具 | 示例输出 4 工具 |
| 3 | 局部编辑 | `EditFileTool` | diff/patch 基础 | old_text 0/多/空测试 | 学习笔记 | 为什么不全局替换 | edit 测试通过 |
| 4 | 结构化结果 | `ToolResult` | OpenTelemetry primer | success/failure 测试 | ADR-0007 | result 和 message 区别 | result 测试通过 |
| 5 | 链路整合 | `_tool_result_to_message` | mini-SWE trajectory | edit 成功/失败集成 | 流程图 | 序列化边界价值 | 集成测试通过 |
| 6 | 文档表达 | 无生产代码 | README/架构表达 | 示例+全量测试 | Week 2 讲解稿 | 如何讲工具链 | 文档同步 |
| 7 | 小加固 | env 输出脱敏 | subprocess/env | secret redaction 测试 | 面试题归档 | 脱敏和审批区别 | 基线通过 |

## Week 3 - Agent Core + Tool Runtime 工业级加固

1. 主题：真实状态纠偏、trace_id、工具统计、输出截断、文件大小限制。
2. 工业级目标：把 Week 1-2 主链从“可运行”升级为“可观测、可控输出、可审计雏形”。
3. 概念：trace_id、tool_call_id、structured logs、output truncation、resource limit。
4. 参考项目：mini-SWE-agent 的 linear trajectory；OpenHands event/trajectory；LangChain tracing。
5. 代码模块：`src/pca/core/events.py`、`src/pca/observability/logger.py`、`src/pca/tools/base.py`、`registry.py`、`file_tools.py`、`shell_runtime.py`。
6. 测试：trace 透传、registry stats、输出截断、大文件拒绝、二进制拒绝。
7. 文档：修正 README/Next Actions 状态，新增 ADR-0008。
8. 验收：全量测试、两个示例、compileall；新增 `examples/03_observed_tool_run.py`。
9. 风险：把 observability 做成 print；输出截断破坏原有测试。
10. 新增能力：一次工具调用有 trace、统计、截断和资源边界。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 状态纠偏 | 修正 `README.md` 和 `docs/09_NEXT_ACTIONS.md`，不改源码 | `docs/12...GAPS.md` | 跑当前全量测试 | 实现日志记录漂移 | 文档为什么不能超前 | 文档与源码一致 |
| 2 | trace 数据结构 | 新增 `src/pca/core/events.py` 的 `TraceContext`、`AgentEvent` | OpenTelemetry trace primer | trace id 格式测试 | ADR-0008 草稿 | trace 和日志区别 | 单测通过 |
| 3 | ToolResult 元数据 | 扩展 `ToolResult`：`trace_id`、`tool_call_id`、`output_truncated`，保留兼容 | LangChain tracing concepts | 旧测试+新字段测试 | 更新 ARCHITECTURE | 如何兼容旧 message | 旧/新测试通过 |
| 4 | Registry 统计 | `ToolRegistry` 增加 stats 和 logger hook | mini-SWE trajectory | success/failure/duration stats 测试 | 学习笔记 | stats 放 registry 还是 tool | stats 测试通过 |
| 5 | 输出截断 | `truncate_output()` 接入 shell/file tool result | OpenHands event payload | 大 stdout 截断测试 | 安全边界记录 | 截断后 LLM 怎么知道 | 截断测试通过 |
| 6 | 文件资源限制 | 文件大小上限、二进制检测 | Python pathlib/stat | read/write/edit 大文件/二进制测试 | ADR 完成 | 文本工具边界是什么 | 文件边界测试通过 |
| 7 | 加固验收 | `examples/03_observed_tool_run.py` | 复盘 Week 3 | 全量+示例+compileall | 面试题待答清单 | 9 维达标还缺什么 | 可进入 Week 4 |

## Week 4 - Permission System

1. 主题：危险命令、文件操作风险、审批流、策略判断。
2. 工业级目标：高风险工具调用执行前可分类、可拒绝、可审批、可审计。
3. 概念：risk level、policy decision、approval request、audit event。
4. 参考项目：Cline approval；OpenHands action security；MCP tool permission 风险。
5. 代码模块：`src/pca/permissions/risk.py`、`policy.py`、`approval.py`、`audit.py`。
6. 测试：safe/ask/deny、危险命令、覆盖写入、审批通过/拒绝。
7. 文档：ADR-0009，权限总链路图。
8. 验收：`run_command` 默认经过 permission gate；危险命令不执行。
9. 风险：只做字符串匹配导致误判；把策略硬编码进 runtime。
10. 新增能力：执行前控制。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 风险分类 | `RiskLevel`、`RiskAssessment`、`classify_command` | Cline approval docs/code | `rm/del/curl/python -c` 分类测试 | 学习笔记 | 分类和拦截区别 | 分类测试通过 |
| 2 | 策略判断 | `PermissionPolicy.decide` | policy engine basics | allow/ask/deny 测试 | ADR-0009 草稿 | risk 和 policy 区别 | 策略测试通过 |
| 3 | 审批对象 | `ApprovalRequest`、`ApprovalDecision` | human-in-the-loop | approve/reject/expired 测试 | 流程图 | 审批为什么要记录理由 | 审批测试通过 |
| 4 | 接入 shell | `ShellCommandTool` 或 registry 前置 permission hook | OpenHands action model | 危险命令不会执行测试 | 更新 ARCHITECTURE | gate 放哪层 | shell gate 通过 |
| 5 | 文件风险 | classify write/edit overwrite/delete-like paths | Aider diff workflow | 覆盖写入 ask 测试 | 记录文件策略 | workspace 和 permission 区别 | 文件风险测试通过 |
| 6 | 审计事件 | `PermissionAuditEvent` 写 JSONL | audit log basics | audit 内容测试 | 实现日志 | audit 和 log 区别 | audit 测试通过 |
| 7 | 验收 | `examples/04_permission_agent.py` | 复盘 Cline | 全量+安全测试 | 面试题 | 如何解释权限系统 | 示例证明拒绝/审批 |

## Week 5 - Workspace / Sandbox / Checkpoint

1. 主题：Workspace abstraction、checkpoint、rollback、sandbox adapter。
2. 目标：文件和命令副作用可隔离、可预览、可回滚。
3. 概念：workspace root、snapshot、git checkpoint、process isolation、resource limit。
4. 参考项目：OpenHands runtime/sandbox/workspace；mini-SWE-agent sandbox。
5. 代码：`src/pca/runtime/workspace.py`、`checkpoints.py`、`docker_runtime.py` 雏形。
6. 测试：checkpoint create/restore、rollback dirty files、sandbox interface fake。
7. 文档：ADR-0010 sandbox 取舍。
8. 验收：危险变更可在临时 workspace 中回滚。
9. 风险：在本机误删文件；Docker 依赖过早。
10. 新增能力：受控 workspace 生命周期。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Workspace 抽象 | `Workspace(root)`、路径解析统一迁移计划 | OpenHands workspace | resolve/inside tests | ADR 草稿 | workspace 和 path helper 区别 | 单测通过 |
| 2 | Checkpoint | `FileCheckpoint` 保存文件快照 | git stash/patch docs | create/restore 测试 | 学习笔记 | snapshot 粒度怎么选 | restore 通过 |
| 3 | Git checkpoint | `GitCheckpoint` 用 diff 记录 | Aider git workflow | dirty tree 测试 | 决策记录 | 为什么优先 git diff | diff 测试通过 |
| 4 | Runtime interface | `CommandRuntime` Protocol | mini-SWE env | fake runtime 测试 | 架构图 | runtime 可替换点 | interface 测试通过 |
| 5 | Sandbox adapter | `DockerRuntime` 占位升级为可检测 adapter | OpenHands sandbox | docker unavailable graceful 测试 | 说明限制 | 没 Docker 如何降级 | graceful pass |
| 6 | Rollback 集成 | permission denied/failed edit 后 rollback | OpenHands event | rollback integration test | 实现日志 | 哪些操作不能自动回滚 | 集成通过 |
| 7 | 验收 | `examples/05_checkpoint_rollback.py` | 复盘 sandbox | 全量+安全测试 | 面试题 | sandbox 不等于权限 | 示例可运行 |

## Week 6 - Tool Runtime 加固周

1. 主题：将 Week 4-5 权限和 workspace 做到可解释、可测、可审计。
2. 目标：安全性、健壮性、可观测性达到阶段验收。
3. 概念：error taxonomy、retry、timeout、audit completeness、resource caps。
4. 参考项目：OpenHands evaluation/runtime；Cline approval UX。
5. 代码：跨 `permissions`、`runtime`、`tools`。
6. 测试：safety regression matrix。
7. 文档：工业级加固报告。
8. 验收：`tests/safety` 全通过，真实小 repo 安全验证报告。
9. 风险：加固时引入行为破坏。
10. 新增能力：安全执行基础达阶段标准。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 现状评估 | 不写功能，列 9 维差距 | `INDUSTRIAL_STANDARDS.md` | 基线测试 | 加固报告初版 | 最大风险是什么 | 差距清单完成 |
| 2 | 错误分类 | `ToolErrorCode`、permission error code | OpenHands errors | error code 测试 | ADR 更新 | 用户错误 vs 系统错误 | 测试通过 |
| 3 | Retry/timeout | 对临时失败定义 retry policy | retry patterns | retry unit tests | 学习笔记 | 何时不该重试 | 测试通过 |
| 4 | Audit 完整性 | audit 覆盖 file/shell/git/memory placeholder | audit patterns | audit matrix test | 更新 EVALUATION | audit 缺字段风险 | matrix 通过 |
| 5 | Safety suite | 新建 `tests/safety/` | Cline/OpenHands security | rm/curl/outside/secret cases | 安全报告 | 安全测试如何命名 | safety 通过 |
| 6 | 真实验证 | 构造 `tmp/demo_repo` 修改任务 | mini-SWE benchmark | e2e safe task | 真实验证报告 | 真实任务暴露了什么 | 报告完成 |
| 7 | 放行复盘 | 修缺口 | 复盘所有 ADR | 全量+compileall | 面试题 | 是否可进入 Coding Agent | 阶段放行 |

## Week 7 - Repo Scanner / Repo Map

1. 主题：代码库理解入口。
2. 目标：Agent 能扫描仓库、忽略噪声、生成稳定 repo map。
3. 概念：file inventory、ignore rules、language detection、summary budget。
4. 参考项目：Aider repo map；mini-SWE-agent benchmark repo handling。
5. 代码：`src/pca/coding/repo_scanner.py`、`repo_map.py`、`file_summary.py`。
6. 测试：忽略 `.git/__pycache__/.venv`、稳定排序、预算截断。
7. 文档：ADR-0011 repo map 设计。
8. 验收：`examples/06_repo_map.py` 输出当前仓库 map。
9. 风险：扫描过大目录或泄漏 ignored 文件。
10. 新增能力：repo awareness。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 文件清单 | `RepoScanner.scan(root)` | Aider repo map | ignore/size tests | ADR 草稿 | 为什么不能扫描全部 | scanner 测试通过 |
| 2 | 语言识别 | suffix/language metadata | pygments/lang docs | py/md/toml tests | notes | 语言识别有何用 | metadata 通过 |
| 3 | 文件摘要 | `FileSummary` 行数/符号粗摘要 | Aider summary | summary tests | docs | 摘要和内容区别 | summary 通过 |
| 4 | Repo map | `RepoMap.build` | Aider repo map | stable order tests | Mermaid | map 为什么稳定排序 | map 通过 |
| 5 | Budget | max files/max chars | context budgeting | truncation tests | eval note | 超预算如何失败 | budget 通过 |
| 6 | 示例 | `examples/06_repo_map.py` | README examples | example test | README 更新 | 外部读者看什么 | 示例可运行 |
| 7 | 复盘 | 小重构 | 复盘 Aider | 全量测试 | 面试题 | repo map 还缺 symbol | 放行 |

## Week 8 - Symbol Index / File Relevance

1. 主题：符号索引和相关文件排序。
2. 目标：从“列文件”进化到“找相关代码”。
3. 概念：AST、symbol、import graph、keyword matching、ranking。
4. 参考项目：Aider file selection；LangChain retriever ranking。
5. 代码：`src/pca/coding/symbol_index.py`、`file_ranker.py`。
6. 测试：函数/类/import 索引，query relevance。
7. 文档：索引格式和限制。
8. 验收：查询“ToolResult”能返回相关源码和测试。
9. 风险：AST parser 失败、排序不稳定。
10. 新增能力：file relevance ranking。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | AST 基础 | `PythonSymbolExtractor` | Python ast docs | function/class tests | notes | AST 失败怎么办 | extractor 通过 |
| 2 | Import graph | 记录 imports/exports | Aider map | import tests | ADR | import 有何价值 | import 通过 |
| 3 | Symbol index | `SymbolIndex.build` | code search patterns | index tests | docs | index 如何更新 | index 通过 |
| 4 | Keyword ranking | `FileRanker.rank(query)` | BM25 intro | keyword tests | notes | 相关性如何评估 | ranking 通过 |
| 5 | Hybrid signals | filename/symbol/import/test proximity | Aider file selection | ranking golden | eval note | 排序会不会漂移 | golden 通过 |
| 6 | 示例 | `examples/07_file_relevance.py` | examples | example test | README | 如何展示能力 | 示例可运行 |
| 7 | 复盘 | 修稳定性 | 复盘 | 全量测试 | 面试题 | 距离真实 code search 差什么 | 放行 |

## Week 9 - Patch / Diff / Git Workflow

1. 主题：代码修改工作流。
2. 目标：生成、应用、审查和回滚 diff。
3. 概念：unified diff、patch apply、conflict、git diff、commit message。
4. 参考项目：Aider diff/edit/git。
5. 代码：`src/pca/coding/patch.py`、`diff_review.py`、`src/pca/tools/git_tools.py`。
6. 测试：patch apply、conflict、git status/diff、commit message candidate。
7. 文档：ADR-0012 patch 策略。
8. 验收：Agent 能修改临时 repo 并输出 diff。
9. 风险：误改文件、patch 模糊应用。
10. 新增能力：可审查代码变更。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | diff 格式 | `UnifiedDiff` parser 最小版 | GNU diff docs | parse tests | ADR 草稿 | diff 比 edit_file 难在哪 | parse 通过 |
| 2 | apply patch | exact context apply | Aider edit | apply/fail tests | notes | 冲突应失败还是猜测 | apply 通过 |
| 3 | diff review | `DiffReview` 风险摘要 | code review docs | added/deleted tests | docs | review 看什么 | review 通过 |
| 4 | git status/diff | `GitTool.status/diff` | git docs | temp repo tests | ADR | shell git vs API | git tests 通过 |
| 5 | commit message | candidate only | Aider commit | message tests | notes | 为什么不自动 commit | message 通过 |
| 6 | 集成示例 | `examples/08_patch_git.py` | Aider workflow | e2e temp repo | README | 如何展示 diff | 示例可运行 |
| 7 | 复盘 | rollback 补强 | 复盘 | 全量测试 | 面试题 | patch 安全边界 | 放行 |

## Week 10 - Test/Lint/Type Runner + Coding Loop

1. 主题：自动验证和修复循环。
2. 目标：Agent 修改后能运行测试、lint、type check，并用失败结果修复。
3. 概念：test command discovery、quality gates、failure parsing、repair loop。
4. 参考项目：Aider test feedback；OpenHands SWE-bench eval。
5. 代码：`src/pca/coding/test_runner.py`、`quality_gate.py`、`repair_loop.py`。
6. 测试：pytest runner、failure capture、lint/type placeholders。
7. 文档：质量门禁策略。
8. 验收：临时 repo bugfix E2E。
9. 风险：无限修复循环、错误解析不稳定。
10. 新增能力：test-driven coding agent loop。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | test runner | `PytestRunner.run` | pytest CLI | pass/fail tests | notes | returncode 怎么用 | runner 通过 |
| 2 | failure parser | parse file/line/error | pytest output | parser golden | docs | parser 失败怎么办 | golden 通过 |
| 3 | quality gate | `QualityGate` 聚合 test/lint/type | CI patterns | gate tests | ADR | gate 放 Agent 还是 CLI | gate 通过 |
| 4 | repair loop | max attempts + failure injection | SWE-bench loop | loop tests | Mermaid | 如何避免盲试 | loop 通过 |
| 5 | lint/type | ruff/mypy optional runner | ruff/mypy docs | unavailable graceful | docs | 可选依赖如何处理 | graceful pass |
| 6 | E2E | 修改临时 repo 函数让测试过 | OpenHands eval | e2e bugfix | report | 过程质量怎么看 | e2e 通过 |
| 7 | 阶段复盘 | 整理 Coding Agent gap | 复盘 Aider/OpenHands | 全量 | 面试题 | 当前能否展示 | 放行 |

## Week 11 - Document Loader / Chunking

1. 主题：RAG 基础：加载和切分。
2. 目标：读取项目文档和个人知识库，生成带 metadata 的 chunk。
3. 概念：Document、metadata、chunk id、text splitter、citation source。
4. 参考项目：LangChain document loaders/splitters；Khoj docs ingestion。
5. 代码：`src/pca/retrieval/document.py`、`loaders.py`、`splitters.py`。
6. 测试：Markdown loader、chunk boundaries、metadata golden。
7. 文档：RAG 数据模型。
8. 验收：加载 `docs/` 并输出 chunks。
9. 风险：chunk 无来源导致引用不可追溯。
10. 新增能力：知识库 ingestion。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Document 模型 | `Document` dataclass | LangChain Document | model tests | ADR | metadata 必须有哪些 | tests pass |
| 2 | Markdown loader | `MarkdownLoader.load` | Khoj docs ingestion | loader tests | notes | loader 失败如何表达 | loader pass |
| 3 | Text loader | `.txt/.py/.md` generic loader | loaders | encoding tests | docs | 代码能否当文档 | pass |
| 4 | Splitter | heading/size splitter | text splitter docs | chunk golden | docs | chunk 太大/小影响 | golden pass |
| 5 | Chunk id | stable id + source metadata | citation docs | stable id test | EVALUATION 更新 | citation 需要什么 | pass |
| 6 | 示例 | `examples/09_load_docs.py` | examples | example test | README | 如何展示 RAG 入口 | runnable |
| 7 | 复盘 | 小重构 | 复盘 | 全量 | 面试题 | RAG 还缺检索 | 放行 |

## Week 12 - BM25 / Vector Retrieval / Rerank

1. 主题：检索引擎。
2. 目标：支持 keyword、vector mock、hybrid、rerank。
3. 概念：BM25、embedding adapter、hybrid score、reranking。
4. 参考项目：Khoj semantic search；LangChain retrievers/vector stores。
5. 代码：`src/pca/retrieval/bm25.py`、`vector.py`、`hybrid.py`、`rerank.py`。
6. 测试：known query recall、score order、empty result。
7. 文档：检索策略。
8. 验收：查询 ADR 能召回对应文档。
9. 风险：真实 embedding 过早引入网络依赖。
10. 新增能力：本地可测试 retrieval。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | BM25 | `BM25Retriever` | BM25 intro | recall tests | notes | BM25 适合什么 | pass |
| 2 | Mock vector | deterministic embedding | vector store docs | vector tests | docs | 为什么先 mock | pass |
| 3 | Hybrid | combine scores | Khoj search | hybrid ranking tests | ADR | 如何调权重 | pass |
| 4 | Rerank | simple heuristic reranker | rerank docs | rerank tests | notes | rerank 何时有用 | pass |
| 5 | Query rewrite | `QueryRewriter` rule-based | LangChain retriever | rewrite tests | docs | rewrite 风险 | pass |
| 6 | 示例 | `examples/10_retrieve_docs.py` | examples | example test | README | 如何展示 citation | runnable |
| 7 | 复盘 | 修空结果 | 复盘 | 全量 | 面试题 | 检索质量如何量化 | 放行 |

## Week 13 - Citation / RAG Answering / Retrieval Eval

1. 主题：带引用回答和检索评估。
2. 目标：RAG 回答必须引用来源，不命中时不编造。
3. 概念：citation、grounded answer、retrieval benchmark、precision/recall。
4. 参考项目：Khoj QA；LangChain RetrievalQA；Zep context assembly。
5. 代码：`src/pca/retrieval/citation.py`、`qa.py`、`eval.py`。
6. 测试：citation format、no-result answer、benchmark metrics。
7. 文档：RAG eval 报告。
8. 验收：问 `ToolResult` 设计能引用 ADR-0007。
9. 风险：LLM 生成无来源答案。
10. 新增能力：可验证 RAG。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Citation | `Citation(source, span)` | citation patterns | format tests | docs | 引用最小字段 | pass |
| 2 | Context pack | `RetrievedContext` | Zep context blocks | pack tests | notes | 上下文如何排序 | pass |
| 3 | QA mock | `RagAnswerer` with mock LLM | Khoj QA | grounded answer tests | docs | answerer 不该做检索吗 | pass |
| 4 | no result | no citation refusal | RAG safety | no-result tests | EVALUATION | 不知道怎么说 | pass |
| 5 | eval set | `benchmarks/retrieval/*.jsonl` | eval docs | metric tests | eval report | 指标选什么 | pass |
| 6 | 示例 | `examples/11_rag_qa.py` | examples | example test | README | 如何展示引用 | runnable |
| 7 | 复盘 | 小重构 | 复盘 | 全量 | 面试题 | RAG 和 memory 区别 | 放行 |

## Week 14 - RAG 加固周

1. 主题：loader/retrieval/citation/eval 加固。
2. 目标：RAG 模块有稳定 golden、评估报告和失败语义。
3. 概念：golden test、regression corpus、citation correctness。
4. 参考项目：Khoj benchmark；LangChain eval patterns。
5. 代码：跨 retrieval 模块。
6. 测试：golden、regression、edge cases。
7. 文档：RAG 工业级差距报告。
8. 验收：retrieval eval 可重复运行。
9. 风险：评估集太小误导质量。
10. 新增能力：RAG 可被验证。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | 现状评估 | 列 9 维差距 | standards | baseline eval | 加固报告 | 最大 RAG 风险 | 清单完成 |
| 2 | loader edge | 编码/空文件/大文件 | loader docs | edge tests | docs | loader 是否跳过 | pass |
| 3 | chunk golden | 固定 chunks | splitter docs | golden tests | docs | golden 何时更新 | pass |
| 4 | retrieval eval | 增加 20 个查询 | eval docs | metric run | report | recall 低怎么办 | report |
| 5 | citation audit | 验证 citation source exists | citation docs | audit tests | EVALUATION | 引用错比无引用更糟吗 | pass |
| 6 | E2E RAG | 当前项目文档问答 | Khoj | e2e tests | report | 能否用于项目继续 | pass |
| 7 | 放行 | 修缺口 | 复盘 | 全量 | 面试题 | 可进入 Memory 吗 | 放行 |

## Week 15 - Memory Store / Write Policy

1. 主题：长期记忆基础。
2. 目标：安全写入和检索用户/项目/任务记忆。
3. 概念：memory candidate、write policy、namespace、evidence、lifecycle。
4. 参考项目：Letta、Mem0。
5. 代码：`src/pca/memory/base.py`、`store.py`、`policy.py`。
6. 测试：write/read/search/update/reject/conflict。
7. 文档：ADR-0013 memory model。
8. 验收：记住并检索“用户偏好中文解释”。
9. 风险：把敏感信息写入长期记忆。
10. 新增能力：长期记忆雏形。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Memory 模型 | `MemoryRecord` | Letta memory | model tests | ADR 草稿 | memory 和 note 区别 | pass |
| 2 | Store | JSONL/SQLite store | Mem0 APIs | write/read tests | docs | 为什么先本地 | pass |
| 3 | Namespaces | preference/project/task/learning | Letta state | namespace tests | notes | 分类错怎么办 | pass |
| 4 | Write policy | candidate/allow/ask/deny | memory lifecycle | policy tests | ADR | 谁决定写入 | pass |
| 5 | Search | keyword search | Mem0 retrieval | search tests | docs | 检索和 RAG 区别 | pass |
| 6 | 示例 | `examples/12_memory_store.py` | examples | example test | README | 如何展示长期记忆 | runnable |
| 7 | 复盘 | secret deny tests | 复盘 | 全量 | 面试题 | 记忆安全边界 | 放行 |

## Week 16 - Project / Learning / Task Memory

1. 主题：个人助理记忆类型。
2. 目标：跟踪项目决策、学习进度、每日任务和下一步。
3. 概念：project state、learning checkpoint、task status、decision record。
4. 参考项目：Khoj personal assistant；Letta stateful agents。
5. 代码：`project_memory.py`、`learning_memory.py`、`task_memory.py`。
6. 测试：记录/更新/查询/压缩。
7. 文档：Memory 使用规则。
8. 验收：能回答“当前 PCA 下一步是什么，依据哪些文件”。
9. 风险：和 docs/09_NEXT_ACTIONS.md 双写漂移。
10. 新增能力：项目连续性。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Project memory | `ProjectMemory` | Khoj docs | project tests | docs | docs 和 memory 谁权威 | pass |
| 2 | Learning memory | day/week progress records | Letta state | progress tests | notes | 学习进度如何更新 | pass |
| 3 | Task memory | task status and blockers | task models | status tests | docs | task 和 todo 区别 | pass |
| 4 | Decision memory | ADR ingestion | ADR patterns | decision tests | ADR | 决策如何引用证据 | pass |
| 5 | Sync policy | docs -> memory read-only sync | sync patterns | drift tests | docs | 如何防双写 | pass |
| 6 | 示例 | `examples/13_project_memory.py` | examples | example test | README | 如何展示连续性 | runnable |
| 7 | 复盘 | 修漂移规则 | 复盘 | 全量 | 面试题 | memory 是否可替代 docs | 放行 |

## Week 17 - Context Compression

1. 主题：短期上下文压缩和摘要。
2. 目标：长轨迹可压缩但保留证据和待办。
3. 概念：conversation summary、tool observation summary、lossy/lossless boundary。
4. 参考项目：Letta context management；LangChain memory summaries。
5. 代码：`src/pca/context/compressor.py`、`summary.py`。
6. 测试：摘要保留任务、决策、错误、引用。
7. 文档：压缩策略。
8. 验收：压缩一段工具轨迹后仍能解释状态。
9. 风险：摘要丢失安全/审批信息。
10. 新增能力：长任务续接。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Summary model | `ConversationSummary` | summary memory | model tests | ADR | 什么不能丢 | pass |
| 2 | Rule compressor | extract facts/actions/errors | Letta context | compressor tests | notes | 规则摘要够吗 | pass |
| 3 | Tool summary | summarize ToolResult list | trajectory docs | tool summary tests | docs | stdout 如何截断 | pass |
| 4 | Memory handoff | summary to memory candidate | memory lifecycle | handoff tests | docs | 何时写长期记忆 | pass |
| 5 | Safety retention | keep approvals/denials/secrets redacted | safety eval | safety tests | EVALUATION | 安全事件能压缩吗 | pass |
| 6 | 示例 | `examples/14_context_compression.py` | examples | example test | README | 如何展示续接 | runnable |
| 7 | 复盘 | 小重构 | 复盘 | 全量 | 面试题 | 压缩损失怎么评估 | 放行 |

## Week 18 - Personal State Graph

1. 主题：个人状态图谱。
2. 目标：把用户、项目、任务、决策、偏好、时间事件建模为图。
3. 概念：entity、relation、event、temporal validity、Graph RAG。
4. 参考项目：Graphiti、Zep。
5. 代码：`src/pca/memory/graph_memory.py`、`src/pca/graph/*`。
6. 测试：实体抽取、关系写入、时间更新、查询。
7. 文档：graph memory 模型。
8. 验收：查询“我在 PCA 为什么暂不接真实 LLM”能返回 ADR 和时间。
9. 风险：图谱过度设计。
10. 新增能力：关系感知个人上下文。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Entity model | `Entity/Relation/Event` | Graphiti README | model tests | ADR | 图谱比表强在哪 | pass |
| 2 | Temporal facts | valid_from/valid_to | Zep temporal graph | temporal tests | docs | 事实会过期吗 | pass |
| 3 | Graph store | SQLite adjacency tables | graph basics | store tests | notes | SQLite 够不够 | pass |
| 4 | Event ingestion | task/ADR/memory events | Graphiti episodes | ingestion tests | docs | event 和 memory 区别 | pass |
| 5 | Query | neighbors/path query | Graph RAG | query tests | docs | 如何避免无关关系 | pass |
| 6 | 示例 | `examples/15_personal_graph.py` | examples | example test | README | 如何展示图谱 | runnable |
| 7 | 复盘 | 加 safety guard | 复盘 | 全量 | 面试题 | 图谱何时不用 | 放行 |

## Week 19 - Planner / Executor / Reviewer

1. 主题：任务规划和执行分层。
2. 目标：复杂任务可拆解、执行、审查、重规划。
3. 概念：planner、executor、reviewer、todo state、replanning。
4. 参考项目：Cline Plan/Act；LangGraph workflow。
5. 代码：`src/pca/core/planner.py`、`executor.py`、`reviewer.py`。
6. 测试：plan schema、todo update、failed step replanning。
7. 文档：planner ADR。
8. 验收：一个 coding task 生成 plan 并逐步执行。
9. 风险：planner 生成空泛步骤。
10. 新增能力：可控多步任务。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Plan model | `Plan/PlanStep` | Cline Plan/Act | model tests | ADR | 好计划什么样 | pass |
| 2 | Todo state | step status transitions | LangGraph state | transition tests | docs | 状态机边界 | pass |
| 3 | Executor | execute one step via tools | mini-SWE loop | executor tests | notes | executor 能否自行改计划 | pass |
| 4 | Reviewer | review diff/test results | code review patterns | reviewer tests | docs | review 何时失败 | pass |
| 5 | Replan | failed step -> revised plan | LangGraph conditional | replan tests | ADR | 如何防无限 replan | pass |
| 6 | 示例 | `examples/16_planner_executor.py` | examples | example test | README | 如何展示 planning | runnable |
| 7 | 复盘 | 加 max attempts | 复盘 | 全量 | 面试题 | planner 和 AgentLoop 区别 | 放行 |

## Week 20 - State Machine / Event System

1. 主题：状态机和事件系统。
2. 目标：把复杂 agent 控制流从单 loop 升级为可恢复 workflow。
3. 概念：node、edge、event、checkpoint、interrupt。
4. 参考项目：LangGraph、OpenHands event stream。
5. 代码：`src/pca/core/state_machine.py`、`events.py`、`runtime/checkpoints.py`。
6. 测试：node transition、checkpoint resume、human interrupt。
7. 文档：state machine 架构图。
8. 验收：审批中断后恢复执行。
9. 风险：状态机过早复杂化。
10. 新增能力：durable workflow。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | State model | `AgentState` | LangGraph state | model tests | ADR | state 最小字段 | pass |
| 2 | Nodes/edges | `StateMachine` | LangGraph nodes | transition tests | docs | edge 如何测试 | pass |
| 3 | Events | `AgentEvent` stream | OpenHands events | event tests | notes | event 和 log 区别 | pass |
| 4 | Checkpoint | save/load state | durable execution | checkpoint tests | docs | 恢复点放哪 | pass |
| 5 | Interrupt | approval interrupt/resume | HITL docs | interrupt tests | ADR | 人工介入如何恢复 | pass |
| 6 | 示例 | `examples/17_state_machine.py` | examples | example test | README | 如何展示 workflow | runnable |
| 7 | 复盘 | 整合 planner | 复盘 | 全量 | 面试题 | 何时不用状态机 | 放行 |

## Week 21 - Observability / Replay

1. 主题：可观测性和回放。
2. 目标：一次任务可按 trace_id 完整复盘。
3. 概念：structured log、trace span、audit log、trajectory replay、stats。
4. 参考项目：OpenHands trajectories；LangChain tracing；mini-SWE-agent linear history。
5. 代码：`src/pca/observability/logger.py`、`tracing.py`、`replay.py`。
6. 测试：trace log、audit log、replay determinism。
7. 文档：observability 使用说明。
8. 验收：`examples/18_trace_replay.py` 可回放 mock 任务。
9. 风险：日志泄漏敏感信息。
10. 新增能力：可复盘 agent。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Structured log | JSON logger | OpenTelemetry logging | logger tests | ADR | print 为什么不够 | pass |
| 2 | Trace spans | `Trace/span` | tracing docs | span tests | docs | span 边界 | pass |
| 3 | Audit log | sensitive operation audit | audit docs | audit tests | notes | audit 保存多久 | pass |
| 4 | Replay | replay messages/tool results | mini trajectory | replay tests | docs | replay 不能重做什么 | pass |
| 5 | Stats | aggregate tool/run stats | metrics docs | stats tests | EVALUATION | 指标如何误导 | pass |
| 6 | 示例 | `examples/18_trace_replay.py` | examples | example test | README | 如何展示 trace | runnable |
| 7 | 复盘 | secret redaction in logs | 复盘 | 全量 | 面试题 | 可观测性差距 | 放行 |

## Week 22 - Evaluation / CI

1. 主题：评估体系和 CI。
2. 目标：项目质量由自动化测试、benchmark 和报告证明。
3. 概念：golden、regression、safety eval、coding benchmark、RAG eval、memory eval。
4. 参考项目：OpenHands evaluation；SWE-bench 思想；AgentLens 过程质量。
5. 代码：`src/pca/evaluation/*`、`.github/workflows/ci.yml`。
6. 测试：eval runner、fixtures、metrics。
7. 文档：CI/CD 策略、评估报告。
8. 验收：本地 CI 命令全部通过；GitHub workflow 存在。
9. 风险：只看 pass rate 不看过程质量。
10. 新增能力：自动质量门禁。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Eval model | `EvalCase/EvalResult` | OpenHands eval | model tests | EVALUATION 更新 | eval case 最小字段 | pass |
| 2 | Golden runner | load/run golden cases | golden testing | runner tests | docs | golden 怎么维护 | pass |
| 3 | Safety eval | dangerous action cases | safety eval | safety runner tests | report | 安全怎么打分 | pass |
| 4 | Coding benchmark | temp repo tasks | SWE-bench | benchmark tests | report | pass 是否足够 | pass |
| 5 | Memory/RAG eval | retrieval/memory metrics | Khoj/Zep eval | metrics tests | report | recall 低怎么办 | pass |
| 6 | CI | `.github/workflows/ci.yml` | GitHub Actions docs | local command check | README badge note | CI 失败如何处理 | workflow created |
| 7 | 复盘 | release quality gate | 复盘 | full CI commands | 面试题 | 作品集如何证明质量 | 放行 |

## Week 23 - CLI / Product Workflow

1. 主题：产品层和 CLI。
2. 目标：用户能通过 CLI 运行真实工作流。
3. 概念：command design、config、doctor、approval prompt、session files。
4. 参考项目：mini-SWE-agent CLI、Aider CLI、Khoj self-host docs。
5. 代码：`src/pca/cli.py`、`config.py`、`session.py`。
6. 测试：CLI help、doctor、dry-run、approval prompt。
7. 文档：用户手册。
8. 验收：`python -m pca.cli doctor` 和一个 dry-run coding task 可运行。
9. 风险：CLI 直接塞业务逻辑。
10. 新增能力：可演示产品入口。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | CLI skeleton | `argparse` commands | mini CLI | help tests | docs | CLI 职责边界 | pass |
| 2 | Config | `Config` env/file/defaults | config patterns | config tests | ADR | 配置优先级 | pass |
| 3 | Doctor | environment checks | Khoj setup docs | doctor tests | README | doctor 检查什么 | pass |
| 4 | Session | session dir + trace file | session design | session tests | docs | session 如何恢复 | pass |
| 5 | Approval prompt | CLI approval input | Cline UX | prompt tests | notes | 非交互如何处理 | pass |
| 6 | Dry run | `pca run --dry-run` | Aider CLI | e2e dry-run | user guide | dry-run 价值 | runnable |
| 7 | 复盘 | polish errors | 复盘 | full tests | 面试题 | 产品工作流是否顺 | 放行 |

## Week 24 - Portfolio Release

1. 主题：最终集成、真实验证、作品集发布。
2. 目标：把项目包装成可展示、可运行、可解释的作品。
3. 概念：release checklist、demo script、architecture narrative、known gaps。
4. 参考项目：Aider/OpenHands/Khoj README 组织方式。
5. 代码：只修 bug 和集成，不新增大模块。
6. 测试：全量、E2E、benchmark、CI。
7. 文档：README、ARCHITECTURE、EVALUATION、portfolio case study。
8. 验收：从干净环境能按 README 跑通核心演示。
9. 风险：文档宣称超过真实能力。
10. 新增能力：作品集展示完成。

| Day | 学习目标 | 代码任务 | 阅读任务 | 测试任务 | 文档任务 | 复盘问题 | 完成标准 |
|---|---|---|---|---|---|---|---|
| 1 | Release audit | 列功能矩阵 | own docs | baseline all tests | release checklist | 哪些不能宣称 | checklist |
| 2 | Demo 1 | repo explanation demo | README examples | demo test | demo script | 读者第一眼看什么 | runnable |
| 3 | Demo 2 | coding fix demo | Aider demos | e2e demo | case study | 如何证明修改真实 | runnable |
| 4 | Demo 3 | memory/RAG demo | Khoj demos | e2e demo | case study | 如何展示个人助理 | runnable |
| 5 | Docs polish | 修 README/ARCHITECTURE/EVALUATION | top repos README | link/test commands | portfolio doc | 文档是否诚实 | docs ready |
| 6 | Final verification | no feature code | release process | pytest/lint/type/e2e/bench | final report | 还有什么风险 | all pass |
| 7 | Closeout | tag/release candidate notes | 复盘 | smoke from clean temp | final interview script | 面试如何讲全项目 | portfolio ready |

## 作品集展示结构

最终作品集页面按以下顺序组织：

1. 一句话：本地优先、可审计的 Personal Coding Assistant。
2. 30 秒 demo GIF 或终端录屏：读仓库、改代码、跑测试、输出 diff。
3. 架构图：Agent Core、Tool Runtime、Permission、Context/RAG、Memory、Evaluation。
4. 工业级证据：测试数量、E2E 场景、安全拒绝、trace/replay、评估报告。
5. 技术深挖：ToolResult、Permission Gate、Repo Map、Memory Write Policy。
6. 已知边界：不是多用户 SaaS，不做企业密钥平台，不承诺完全替代成熟 Agent。
