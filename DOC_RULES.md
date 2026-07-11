# Document Rules

本文件只定义文档写入、归档和反漂移规则，不保存当前状态。当前状态、测试基线、阻塞项和下一步只维护在 `docs/09_NEXT_ACTIONS.md`，该文件是唯一实时状态源。

## 权威位置

| 信息类型 | 权威位置 | 写入规则 |
|---|---|---|
| 当前状态和下一步 | `docs/09_NEXT_ACTIONS.md` | 唯一实时状态源；维护当前能力边界摘要、课程门禁、阻塞项和下一条用户指令 |
| 当前活跃日任务 | `docs/02_DAILY_TASKS.md` | 只保留当前任务、复盘问题和待回答面试题 |
| 实现历史和验证证据 | `docs/07_IMPLEMENTATION_LOG.md` | 活跃日志保持短小，历史内容移入 `docs/archive/implementation_log/` |
| 当前模块学习笔记 | `docs/05_LEARNING_NOTES.md` | 只写当前模块，历史笔记移入 `docs/archive/learning_notes/` |
| 架构决策 | `docs/06_ARCHITECTURE_DECISIONS.md` | 只有影响架构边界或长期取舍时新增 ADR |
| 已回答面试题 | `docs/Compilation-of-Interview-Questions.md` | 只归档用户已经回答的问题，必须包含用户回答和标准回答 |
| 路线和阶段目标 | `docs/01_LEARNING_ROADMAP.md`、`docs/14_24_WEEK_PLAN.md` | 路线变更时同步更新入口和完整计划 |
| 已实现能力和差距 | `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md` | 保存详细源码与测试证据及工业级差距；不保存课程门禁或实时数字 |
| 记忆系统边界 | `docs/15_MEMORY_SYSTEM.md` | 定义项目协作记忆、Codex 外部记忆、事实恢复、冲突裁决、结束回写及未来运行时记忆边界；不保存实时状态 |
| 教学协作流程 | `docs/16_TEACHING_WORKFLOW.md` | 只定义稳定教学流程和收口门禁，不保存实时状态 |
| 已实现模块流程与工程作用 | `docs/18_IMPLEMENTED_MODULE_FLOWS.md` | 只描述有源码和测试证据的模块；未完整接线时标“部分实现”或“未接入主链”；不保存实时数字 |
| 日期化代码完成度审计 | `docs/19_CODE_COMPLETION_AUDIT_YYYY-MM-DD.md` | 保存审计当日证据和整改建议，不是实时状态源 |

## 项目记忆文件

这些文件共同构成项目协作记忆，但只有一个文件能保存实时状态：

| 文件 | 角色 | 是否保存实时状态 |
|---|---|---|
| `AGENTS.md` | 会话执行规则和启动读取顺序 | 否 |
| `docs/INDEX.md` | 文档导航入口 | 否 |
| `docs/09_NEXT_ACTIONS.md` | 当前状态、阻塞项、测试基线、下一步 | 是 |
| `docs/02_DAILY_TASKS.md` | 当前活跃日任务、复盘问题、待生成或待回答面试题 | 只保存当日任务状态 |
| `docs/07_IMPLEMENTATION_LOG.md` | 已完成工作的验证证据和交接记录 | 否 |
| `DOC_RULES.md` | 文档写入、归档和反漂移规则 | 否 |
| `docs/15_MEMORY_SYSTEM.md` | 项目协作记忆、Codex 外部记忆、事实恢复、冲突裁决、结束回写及未来运行时记忆边界 | 否 |
| `docs/16_TEACHING_WORKFLOW.md` | 教学协作流程、用户先写代码流程、每日收口门禁 | 否 |

## 写入规则

- 启动读取顺序只维护在 `AGENTS.md`，其他文档不要复制一份。
- README、路线、项目背景只引用 `docs/09_NEXT_ACTIONS.md`，不要复制测试数字、阻塞项或完整能力清单。
- README、ARCHITECTURE 不复制详细模块图；需要实现流程时引用 `docs/18_IMPLEMENTED_MODULE_FLOWS.md`。
- 记忆系统说明只维护在 `docs/15_MEMORY_SYSTEM.md`，不要重新创建根目录 `MEMORY.md` 作为第二状态源。
- 教学协作流程只维护在 `docs/16_TEACHING_WORKFLOW.md`，不要把当前周次或测试数字写进去。
- 每次完成文档、代码或验证任务后，至少检查 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md` 是否需要同步。
- 未回答的面试题必须留在 `docs/09_NEXT_ACTIONS.md` 或 `docs/02_DAILY_TASKS.md`，不得归档到 `docs/Compilation-of-Interview-Questions.md`。
- 占位目录、计划模块、未接入主链的代码，必须明确写成“占位”“计划”或“未接入主链”，不能宣传为已实现能力。
- 模块图谱不得为纯占位模块绘制实现链路；有源码和测试证据但未完整接线时，可以记录局部真实链路，但必须标“部分实现”或“未接入主链”，不得描述为完整产品主链。
- `docs/09_NEXT_ACTIONS.md` 只保存当前能力边界摘要和课程门禁；详细源码与测试证据写入 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md` 或 `docs/18_IMPLEMENTED_MODULE_FLOWS.md`。若描述冲突，以当前源码与本次验证裁决并修正过期文档。
- 日期化审计保留审计当日证据与整改建议，不得回填为当前测试基线或课程实时状态。
- 验证结果必须写具体命令和结果，不写“应该通过”“理论上可用”。

## 归档规则

- `docs/02_DAILY_TASKS.md` 超过 200 行时，归档历史任务。
- `docs/05_LEARNING_NOTES.md` 超过 100 行时，归档历史笔记。
- `docs/07_IMPLEMENTATION_LOG.md` 超过 100 行时，归档旧实现记录。
- `docs/09_NEXT_ACTIONS.md` 超过 50 行时，删除展开预告或移到对应任务文件。
- `docs/15_MEMORY_SYSTEM.md` 只保存稳定边界；如果开始记录实时状态，必须拆回 `docs/09_NEXT_ACTIONS.md`。

## 反漂移检查

修改文档后至少检查：

```powershell
Select-String -Path README.md,docs\00_PROJECT_CONTEXT.md,docs\01_LEARNING_ROADMAP.md -Pattern "当前阶段：|当前主题：|阻塞项：|passed|skipped"
Select-String -Path docs\09_NEXT_ACTIONS.md,docs\02_DAILY_TASKS.md -Pattern "待回答且未归档|尚未回答|不能推进|待用户回答"
Select-String -Path AGENTS.md,docs\INDEX.md,DOC_RULES.md,docs\15_MEMORY_SYSTEM.md,docs\16_TEACHING_WORKFLOW.md -Pattern "实时状态|当前状态|测试基线|阻塞项"

$flows = Get-Content -Raw -Encoding UTF8 docs\18_IMPLEMENTED_MODULE_FLOWS.md
$flowDiagrams = @([regex]::Matches($flows, '(?s)```mermaid\s*(.*?)```') | ForEach-Object { ($_.Groups[1].Value -replace '\s+', ' ').Trim() })
foreach ($path in @('README.md', 'ARCHITECTURE.md')) {
    $rootDoc = Get-Content -Raw -Encoding UTF8 $path
    $rootDiagrams = @([regex]::Matches($rootDoc, '(?s)```mermaid\s*(.*?)```') | ForEach-Object { ($_.Groups[1].Value -replace '\s+', ' ').Trim() })
    if ($rootDiagrams | Where-Object { $flowDiagrams -contains $_ }) { throw "$path 复制了 docs/18 的详细模块图" }
}

$placeholderSection = [regex]::Match($flows, '(?s)## 明确不绘制实现流程的占位模块.*$').Value
if (-not $placeholderSection) { throw 'docs/18 缺少纯占位模块边界章节' }
if ($placeholderSection -match '```mermaid|flowchart|-->') { throw 'docs/18 为纯占位模块绘制了实现链路' }

$auditFiles = @(Get-ChildItem docs -File -Filter '19_CODE_COMPLETION_AUDIT_????-??-??.md')
if (-not $auditFiles) { throw '缺少日期化 docs/19 审计文件' }
foreach ($auditFile in $auditFiles) {
    $audit = Get-Content -Raw -Encoding UTF8 $auditFile.FullName
    if ($audit -notmatch '不是实时状态源') { throw "$($auditFile.Name) 缺少非实时状态声明" }
    if ($audit -match '(?m)^## 当前状态|^## 下一步行动') { throw "$($auditFile.Name) 出现实时状态章节" }
}
```

判断标准：

- `README.md`、`docs/00_PROJECT_CONTEXT.md`、`docs/01_LEARNING_ROADMAP.md` 不应保存当前测试数字或阻塞项。
- `README.md`、`ARCHITECTURE.md` 不应复制 `docs/18_IMPLEMENTED_MODULE_FLOWS.md` 的详细模块图。
- `docs/18_IMPLEMENTED_MODULE_FLOWS.md` 不应为纯占位模块绘制实现链路，也不应保存实时测试数字；有源码和测试但未完整接线的链路必须明确标为“部分实现”或“未接入主链”。
- `docs/19_CODE_COMPLETION_AUDIT_YYYY-MM-DD.md` 只代表审计当日快照，不得覆盖 `docs/09_NEXT_ACTIONS.md` 的实时状态。
- 旧周次、旧 Day 门禁只能出现在实现日志或归档文件中，不能出现在当前状态入口和活跃任务。
- `AGENTS.md` 可以定义启动读取顺序；其他文件只能引用它，不能复制一套新的启动规则。
- `docs/16_TEACHING_WORKFLOW.md` 可以定义教学步骤，但不能保存当前 Week/Day 状态。
