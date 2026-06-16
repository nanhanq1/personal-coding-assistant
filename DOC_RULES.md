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

## 写入规则

- 启动读取顺序只维护在 `AGENTS.md`，其他文档不要复制一份。
- README、路线、项目背景只引用 `docs/09_NEXT_ACTIONS.md`，不要复制测试数字、阻塞项或完整能力清单。
- 每次完成文档、代码或验证任务后，至少检查 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md` 是否需要同步。
- 未回答的面试题必须留在 `docs/09_NEXT_ACTIONS.md` 或 `docs/02_DAILY_TASKS.md`，不得归档到 `docs/Compilation-of-Interview-Questions.md`。
- 占位目录、计划模块、未接入主链的代码，必须明确写成“占位”“计划”或“未接入主链”，不能宣传为已实现能力。
- 验证结果必须写具体命令和结果，不写“应该通过”“理论上可用”。

## 归档规则

- `docs/02_DAILY_TASKS.md` 超过 200 行时，归档历史任务。
- `docs/05_LEARNING_NOTES.md` 超过 100 行时，归档历史笔记。
- `docs/07_IMPLEMENTATION_LOG.md` 超过 100 行时，归档旧实现记录。
- `docs/09_NEXT_ACTIONS.md` 超过 50 行时，删除展开预告或移到对应任务文件。

## 反漂移检查

修改文档后至少检查：

```powershell
Select-String -Path docs\09_NEXT_ACTIONS.md -Pattern "Week 3 Day 2 已开始" -SimpleMatch
Select-String -Path docs\09_NEXT_ACTIONS.md -Pattern "面试题尚未回答|不能推进 Day 2" -SimpleMatch
Select-String -Path README.md,docs\00_PROJECT_CONTEXT.md,docs\01_LEARNING_ROADMAP.md -Pattern "passed|skipped" -SimpleMatch
```
