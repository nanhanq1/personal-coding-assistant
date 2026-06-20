# Weekly Sprints

本文件保留活跃 Sprint 入口。完整 24 周计划见 `docs/14_24_WEEK_PLAN.md`。

## Sprint 共同原则

- 每周交付一个可运行、可测试、可验收的能力切片。
- 每周至少覆盖一个失败路径或安全边界。
- 每周更新测试、文档、实现日志、下一步行动和面试题状态。
- 每 2 周实现后安排 1 周工业级加固；加固周不新增大模块。
- 文档不能宣称源码没有实现的能力。

## 当前 Sprint：Week 4 - Permission System

### 1. 本周主题

为工具执行增加执行前控制基础：风险分类、策略判断、审批对象、shell gate、文件风险和审计事件。

### 2. 本周工业级目标

- 高风险工具调用在执行前可分类。
- 权限策略能返回 allow / ask / deny。
- 审批决策有结构化对象和可审计记录。
- `run_command` 后续默认经过 permission gate。
- 危险命令不应直接执行。

### 3. 核心概念

- risk level
- policy decision
- approval request
- audit event
- permission gate

### 4. 参考项目

- Cline approval：工具执行前的人类审批。
- OpenHands action security：动作安全边界。
- MCP tool permission：工具权限风险建模。

### 5. 代码模块

- `src/pca/permissions/risk.py`
- `src/pca/permissions/policy.py`
- `src/pca/permissions/approval.py`
- `src/pca/permissions/audit.py`
- `src/pca/tools/shell_tools.py`

### 6. 测试任务

- safe / ask / deny 风险分类测试。
- `PermissionPolicy.decide(...)` 测试。
- 审批通过、拒绝、过期测试。
- 危险命令不会执行的集成测试。
- 文件覆盖写入风险测试。
- audit JSONL 内容测试。

### 7. 文档任务

- 更新 `docs/09_NEXT_ACTIONS.md`。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`。
- 新增或更新 ADR-0009。
- 更新权限总链路图。
- Week 4 完成后生成面试题。

### 8. 验收标准

```powershell
E:\python\Scripts\pytest.exe -q
python examples\01_minimal_agent.py
python examples\02_tool_agent.py
python examples\03_observed_tool_run.py
python -m compileall src examples -q
```

后续新增示例：

```powershell
python examples\04_permission_agent.py
```

### 9. 常见风险

- 只做字符串匹配导致大量误判。
- 把策略硬编码进 runtime，导致后续不可替换。
- 把执行后脱敏误当成执行前权限控制。
- 过早接入 shell gate，导致风险分类 API 还没稳定就影响主链。

### 10. 本周完成后新增能力

工具调用具备执行前控制基础：可以先分类风险，再由策略决定允许、询问或拒绝，并留下审计证据。

## 当前周每日安排

| Day | 学习目标 | 代码任务 | 测试任务 | 文档任务 | 完成标准 |
|---|---|---|---|---|---|
| 1 | 风险分类 | `RiskLevel`、`RiskAssessment`、`classify_command` | `rm/del/curl/python -c` 分类测试 | 学习笔记 | 分类测试通过 |
| 2 | 策略判断 | `PermissionPolicy.decide` | allow/ask/deny 测试 | ADR-0009 草稿 | 策略测试通过 |
| 3 | 审批对象 | `ApprovalRequest`、`ApprovalDecision` | approve/reject/expired 测试 | 流程图 | 审批测试通过 |
| 4 | 接入 shell | `ShellCommandTool` 或 registry 前置 permission hook | 危险命令不会执行测试 | 更新 ARCHITECTURE | shell gate 通过 |
| 5 | 文件风险 | classify write/edit overwrite/delete-like paths | 覆盖写入 ask 测试 | 记录文件策略 | 文件风险测试通过 |
| 6 | 审计事件 | `PermissionAuditEvent` 写 JSONL | audit 内容测试 | 实现日志 | audit 测试通过 |
| 7 | 验收 | `examples/04_permission_agent.py` | 全量+安全测试 | 面试题 | 示例证明拒绝/审批 |
