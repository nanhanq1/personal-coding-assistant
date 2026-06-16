# Learning Roadmap

## 路线定位

本项目路线已从原 12 周学习计划重构为 **24 周工业级项目路线**。路线目标不是覆盖概念，而是持续交付一个可运行、可测试、可审计、可展示的 **Personal Coding Assistant**。

完整路线见：`docs/14_24_WEEK_PLAN.md`。

## 为什么扩展为 24 周

原 12 周路线能覆盖 Agent Loop、Tool System、Permission、Context、RAG、MCP、Memory 和 Observability 的概念，但不足以把以下内容做到作品集级别：

- Coding Agent：repo map、symbol index、patch/diff、git workflow、test/lint/type runner、真实代码任务验证。
- Personal Assistant：长期记忆、个人知识库、学习进度、项目决策、任务状态、上下文压缩、个人状态图谱。
- Retrieval/RAG：loader、chunking、BM25、vector retrieval、rerank、citation、retrieval evaluation。
- 工业级能力：权限审批、sandbox、checkpoint/rollback、日志、trace、审计、CI/CD、E2E、benchmark、release checklist。

因此路线采用 24 周，让学习、实现、加固、评估和作品集展示都能落到具体文件、测试和验收标准。

## 当前状态入口

当前状态、测试基线、阻塞项和下一步只维护在 `docs/09_NEXT_ACTIONS.md`。

已实现主线与工业级差距见 `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md`。

## 24 周阶段

| 阶段 | 周次 | 主题 | 核心成果 |
|---|---:|---|---|
| A | 1-3 | Agent Core + Tool Runtime 基线与加固 | 当前主链、trace、输出截断、资源边界 |
| B | 4-6 | Permission + Sandbox + Git Safety | 危险命令分类、审批、审计、checkpoint、rollback |
| C | 7-10 | Coding Agent | repo map、symbol index、patch/diff、test/lint/type/git workflow |
| D | 11-14 | Retrieval / RAG | loader、chunking、BM25/vector、rerank、citation、RAG eval |
| E | 15-18 | Personal Assistant Memory | preference/project/task/learning memory、context compression、state graph |
| F | 19-20 | Planner / State Machine / Events | planner/executor/reviewer、durable workflow、interrupt |
| G | 21-22 | Evaluation / Observability / CI | golden/regression/safety/e2e/eval harness、trace、CI |
| H | 23-24 | Productization / Portfolio | CLI、真实验证、release checklist、作品集文档 |

## 本路线的工业级验收规则

每周必须包含：

1. 本周主题
2. 本周工业级目标
3. 核心概念
4. 参考开源项目
5. 代码模块
6. 测试
7. 文档
8. 验收标准
9. 常见风险
10. 本周新增能力

每日必须包含：

1. 学习目标
2. 代码任务
3. 阅读任务
4. 测试任务
5. 文档任务
6. 复盘问题
7. 完成标准

## 权威文档

- 最终需求：`PROJECT_REQUIREMENTS.md`
- 目标架构：`ARCHITECTURE.md`
- 评估策略：`EVALUATION.md`
- 参考项目映射：`docs/13_REFERENCE_PROJECT_MAPPING.md`
- 完整 24 周计划：`docs/14_24_WEEK_PLAN.md`
- 记忆系统边界：`docs/15_MEMORY_SYSTEM.md`
- 当前下一步：`docs/09_NEXT_ACTIONS.md`
