# 文档索引

本文件是唯一文档导航入口。会话启动读取顺序以 `AGENTS.md` 为准。

## 常驻读取

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | 核心执行规则 |
| `docs/INDEX.md` | 本文件 |
| `docs/09_NEXT_ACTIONS.md` | 当前状态、阻塞项和下一步 |

## 根目录保留入口

| 文件 | 用途 |
|---|---|
| `README.md` | 项目介绍和快速运行 |
| `PROJECT_REQUIREMENTS.md` | 最终项目需求、用户故事和验收定义 |
| `ARCHITECTURE.md` | 当前真实架构、目标架构和模块边界 |
| `EVALUATION.md` | 测试、评估、benchmark 和 CI 策略 |
| `DOC_RULES.md` | 文档写入、归档和反漂移规则 |

## 按需读取

| 文件 | 用途 |
|---|---|
| `docs/00_PROJECT_CONTEXT.md` | 项目背景 |
| `docs/01_LEARNING_ROADMAP.md` | 24 周路线入口 |
| `docs/02_DAILY_TASKS.md` | 当前活跃任务 |
| `docs/03_WEEKLY_SPRINTS.md` | 当前 Sprint |
| `docs/05_LEARNING_NOTES.md` | 当前模块学习笔记 |
| `docs/INDUSTRIAL_STANDARDS.md` | 工业级加固标准 |
| `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md` | 已实现主线和工业级差距 |
| `docs/13_REFERENCE_PROJECT_MAPPING.md` | 外部参考项目到本项目模块的映射 |
| `docs/14_24_WEEK_PLAN.md` | 完整 24 周工业级路线和每日任务 |

## 代码实现时读取

| 文件 | 用途 |
|---|---|
| `docs/06_ARCHITECTURE_DECISIONS.md` | 架构决策记录 |
| `docs/07_IMPLEMENTATION_LOG.md` | 当前实现日志 |
| `docs/04_RESOURCE_LIBRARY.md` | 资料库 |
| `docs/CODEX_PROJECT_BRIEF.md` | 长期项目提示词 |

## 面试相关

| 文件 | 用途 |
|---|---|
| `docs/Compilation-of-Interview-Questions.md` | 已回答面试题汇总 |
| `docs/08_INTERVIEW_BANK.md` | 模块级题库 |
| `docs/10_WEEK1_INTERVIEW_SCRIPT.md` | 第 1 周面试讲解稿 |
| `docs/11_WEEK2_INTERVIEW_SCRIPT.md` | 第 2 周面试讲解稿 |

## 历史归档

| 目录 | 用途 |
|---|---|
| `docs/archive/daily_tasks/` | 历史每日任务 |
| `docs/archive/implementation_log/` | 历史实现日志 |
| `docs/archive/learning_notes/` | 历史学习笔记 |

## 归档规则

- 每周结束时，把当周历史内容移到 `docs/archive/` 对应目录。
- 活跃文件保持短小：`docs/02_DAILY_TASKS.md` ≤ 200 行，`docs/05_LEARNING_NOTES.md` ≤ 100 行，`docs/07_IMPLEMENTATION_LOG.md` ≤ 100 行，`docs/09_NEXT_ACTIONS.md` ≤ 50 行。
- 超过行数上限时必须立即归档，不能等。
