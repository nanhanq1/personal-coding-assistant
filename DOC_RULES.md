# Document Rules

本文件只定义文档写入、归档和反漂移规则，不保存当前状态。当前状态、测试基线、阻塞项和下一步只维护在 `docs/09_NEXT_ACTIONS.md`。

## 权威位置

| 信息类型 | 权威位置 | 写入规则 |
|---|---|---|
| 当前状态和下一步 | `docs/09_NEXT_ACTIONS.md` | 只在这里维护最新状态、阻塞项和下一条用户指令 |
| 当前活跃日任务 | `docs/02_DAILY_TASKS.md` | 只保留当前任务、复盘问题和待回答面试题 |
| 实现历史和验证证据 | `docs/07_IMPLEMENTATION_LOG.md` | 活跃日志保持短小，历史内容移入 `docs/archive/implementation_log/` |
| 当前模块学习笔记 | `docs/05_LEARNING_NOTES.md` | 只写当前模块，历史笔记移入 `docs/archive/learning_notes/` |
| 架构决策 | `docs/06_ARCHITECTURE_DECISIONS.md` | 只有影响架构边界或长期取舍时新增 ADR |
| 已回答面试题 | `docs/Compilation-of-Interview-Questions.md` | 只归档用户已经回答的问题，必须包含用户回答和标准回答 |
| 路线和阶段目标 | `docs/01_LEARNING_ROADMAP.md`、`docs/14_24_WEEK_PLAN.md` | 路线变更时同步更新入口和完整计划 |
| 已实现能力和差距 | `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md` | 只写能从当前源码或测试证明的能力 |
| 记忆系统边界 | `docs/15_MEMORY_SYSTEM.md` | 只定义项目协作记忆和未来运行时记忆边界，不保存实时状态 |

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
| `docs/15_MEMORY_SYSTEM.md` | 项目协作记忆与未来运行时记忆边界 | 否 |

## 写入规则

- 启动读取顺序只维护在 `AGENTS.md`，其他文档不要复制一份。
- README、路线、项目背景只引用 `docs/09_NEXT_ACTIONS.md`，不要复制测试数字、阻塞项或完整能力清单。
- 记忆系统说明只维护在 `docs/15_MEMORY_SYSTEM.md`，不要重新创建根目录 `MEMORY.md` 作为第二状态源。
- 每次完成文档、代码或验证任务后，至少检查 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md` 是否需要同步。
- 未回答的面试题必须留在 `docs/09_NEXT_ACTIONS.md` 或 `docs/02_DAILY_TASKS.md`，不得归档到 `docs/Compilation-of-Interview-Questions.md`。
- 占位目录、计划模块、未接入主链的代码，必须明确写成“占位”“计划”或“未接入主链”，不能宣传为已实现能力。
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
Select-String -Path docs\09_NEXT_ACTIONS.md,docs\02_DAILY_TASKS.md -Pattern "Week 3 Day 2|不能推进 Day 2|面试题尚未回答"
Select-String -Path AGENTS.md,docs\INDEX.md,DOC_RULES.md,docs\15_MEMORY_SYSTEM.md -Pattern "启动读取顺序|实时状态|当前状态"
```

判断标准：

- `README.md`、`docs/00_PROJECT_CONTEXT.md`、`docs/01_LEARNING_ROADMAP.md` 不应保存当前测试数字或阻塞项。
- 旧周次、旧 Day 门禁只能出现在实现日志或归档文件中，不能出现在当前状态入口和活跃任务。
- `AGENTS.md` 可以定义启动读取顺序；其他文件只能引用它，不能复制一套新的启动规则。
