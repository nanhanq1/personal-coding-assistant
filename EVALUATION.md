# Evaluation Strategy

## 目标

评估体系证明两件事：

1. 功能正确：模块行为、集成链路和 E2E 工作流按预期运行。
2. Agent 质量可解释：不是只看最终测试是否通过，还要看探索、修改、验证、权限和记忆写入过程是否合理。

## 测试分层

| 层级 | 目录 | 目标 | 示例 |
|---|---|---|---|
| Unit | `tests/` 或后续 `tests/unit/` | 验证单个函数/类边界 | `ToolParameter.validate`、`RiskClassifier.classify` |
| Integration | `tests/integration/` | 验证模块协作 | `AgentLoop + ToolRegistry + PermissionPolicy` |
| E2E | `tests/e2e/` | 验证真实任务闭环 | 在临时 Python repo 修改函数并跑测试 |
| Golden | `tests/golden/` | 固定稳定输入输出 | repo map 输出、chunking 输出、RAG citation |
| Regression | `tests/regression/` | 防止已修复 bug 回归 | `old_text` 多处命中、env secret 泄漏 |
| Safety | `tests/safety/` | 验证拒绝和审批 | `rm -rf`、越界路径、secret 输出 |
| Benchmark | `benchmarks/` | 衡量质量和性能 | coding task benchmark、retrieval quality、memory recall |

### Safety suite 运行约定

Week 6 Day 5 的 `tests/safety/` 只验证已有安全边界，不执行真实网络请求或真实删除命令：

- shell 拒绝场景注入 `RecordingRuntime`，通过 `calls == []` 证明没有进入执行层。
- 文件场景使用 pytest 临时工作区和真实 sentinel 文件，断言越界、覆盖和删除式编辑没有副作用。
- secret redaction 只调用本地 `ShellRuntime` 的 list-command 路径；敏感值在失败信息和 audit JSONL 中都不得出现。
- 每个失败路径优先断言 `ToolResult.error_code`，再断言固定风险规则和 audit 的 `executed` 状态。

## 模块评估

### Agent Core

- 正常路径：`user -> assistant tool_call -> tool result -> assistant final`
- 停止条件：无 tool call、`max_turns`、tool failure recovery、future stop reason
- 轨迹质量：每个工具结果必须写回 message history
- 回归：未知工具不崩溃，LLM 非 Message 返回稳定失败

### Tool Runtime

- schema：必填参数、类型、额外字段策略
- 文件工具：越界路径、目录读取、二进制检测、大文件限制、局部编辑冲突
- shell：cwd 边界、timeout、输出截断、env 脱敏、危险命令审批
- git：dirty tree、diff、commit message、rollback

### Coding Agent

- repo scanner：忽略 `.git`、缓存、虚拟环境、大文件
- repo map：稳定排序、符号摘要、预算限制
- patch：只修改目标文件、生成可读 diff、冲突时失败
- test runner：捕获 stdout/stderr/returncode/timed_out
- quality loop：测试失败后可进入受控修复流程

### Retrieval / RAG

- chunking golden tests：同一文档输出稳定 chunk id 和 metadata
- BM25/vector recall：查询能召回标注文档
- reranking：相关片段排序提升
- citation：回答必须能指向文件、chunk、行号或文档 id
- failure：检索无结果时不编造引用

### Memory

- write policy：候选记忆、批准、拒绝、更新、冲突
- preference recall：偏好能在相关任务中被检索
- project memory：ADR、任务状态和学习进度可按项目查询
- lifecycle：过期、替换、合并和证据保留
- safety：敏感信息不进入长期记忆

### Observability

- trace：一次 run 可重建消息、工具、权限、测试、memory write
- audit：写文件、shell、git、memory write 都有审计事件
- replay：mock LLM 轨迹可回放
- stats：工具调用次数、失败率、耗时分布、截断次数

## E2E 场景

| 场景 | 输入 | 验收 |
|---|---|---|
| 解释仓库 | “解释这个 repo 的结构和下一步” | 输出 repo map、关键文件、当前状态，不修改文件 |
| 小修复 | 临时 repo 中测试失败 | Agent 定位文件、局部编辑、跑测试，输出 diff |
| 安全拒绝 | 要求删除工作区外文件 | 返回拒绝和理由，无副作用 |
| RAG 问答 | 问项目文档中的架构决策 | 回答带 citation，不编造 |
| 记忆回忆 | 问“我上次为什么选择 ToolResult” | 从项目记忆返回 ADR 摘要和来源 |

## CI 策略

第一阶段 CI：

```text
python -m pytest -q
python -m compileall src examples -q
python examples/01_minimal_agent.py
python examples/02_tool_agent.py
```

第二阶段 CI：

```text
python -m pytest -q
python -m pytest tests/safety -q
python -m pytest tests/integration -q
python -m compileall src examples -q
python -m pca.cli doctor
```

第三阶段 CI：

```text
ruff check .
mypy src
pytest --cov=src/pca --cov-report=term-missing
pytest tests/e2e -q
python -m pca.evaluation.run benchmarks/coding_tasks
python -m pca.evaluation.run benchmarks/retrieval
python -m pca.evaluation.run benchmarks/memory
```

## 通过标准

- 单元和集成测试全部通过。
- 核心模块覆盖率逐步达到 90%，安全边界路径必须有测试。
- E2E 至少覆盖 5 个真实工作流。
- RAG 和 Memory 必须有可重复 benchmark，不以主观感觉判断。
- 安全评估必须证明危险操作不会静默执行。
- 评估报告必须写入 `docs/07_IMPLEMENTATION_LOG.md` 或后续 `docs/evaluation_reports/`。
