# 文档索引

本文件是项目文档的快速导航。大模型每次会话应先读本文件，再按需读取其他文件。

## 常驻读取（每次会话必读，约 200 行）

| 文件 | 行数 | 用途 |
|---|---|---|
| `AGENTS.md` | ~76 | 核心执行规则 |
| `docs/INDEX.md` | ~60 | 本文件 |
| `docs/09_NEXT_ACTIONS.md` | ~40 | 当前状态和下一步 |

## 按需读取（开始新模块时读取）

| 文件 | 行数 | 用途 |
|---|---|---|
| `docs/00_PROJECT_CONTEXT.md` | ~30 | 项目背景 |
| `docs/01_LEARNING_ROADMAP.md` | ~100 | 12 周路线 |
| `docs/02_DAILY_TASKS.md` | ~120 | 当前周任务 |
| `docs/03_WEEKLY_SPRINTS.md` | ~200 | 周冲刺计划 |
| `docs/05_LEARNING_NOTES.md` | ~50 | 当前模块学习笔记 |
| `docs/INDUSTRIAL_STANDARDS.md` | ~290 | 工业级加固标准（P3 详细规范） |
| `docs/12_IMPLEMENTED_ARCHITECTURE_AND_INDUSTRIAL_GAPS.md` | ~435 | 已实现架构和工业级差距 |

## 代码实现时读取

| 文件 | 行数 | 用途 |
|---|---|---|
| `docs/06_ARCHITECTURE_DECISIONS.md` | ~240 | 架构决策记录（ADR） |
| `docs/07_IMPLEMENTATION_LOG.md` | ~50 | 当前周实现日志 |
| `docs/04_RESOURCE_LIBRARY.md` | ~150 | 资料库 |
| `docs/CODEX_PROJECT_BRIEF.md` | ~335 | 完整长期提示词 |

## 面试相关

| 文件 | 行数 | 用途 |
|---|---|---|
| `docs/Compilation-of-Interview-Questions.md` | ~380 | 每日面试题汇总 |
| `docs/08_INTERVIEW_BANK.md` | ~40 | 模块级题库 |
| `docs/10_WEEK1_INTERVIEW_SCRIPT.md` | ~100 | 第 1 周面试讲解稿 |
| `docs/11_WEEK2_INTERVIEW_SCRIPT.md` | ~70 | 第 2 周面试讲解稿 |

## 历史归档（仅在回顾时读取）

| 目录 | 用途 |
|---|---|
| `docs/archive/daily_tasks/` | 历史每日任务 |
| `docs/archive/implementation_log/` | 历史实现日志 |
| `docs/archive/learning_notes/` | 历史学习笔记 |

## 归档规则

- 每周结束时，把当周的历史内容移到 `docs/archive/` 对应目录
- 活跃文件保持短小：02 ≤ 200行，05 ≤ 100行，07 ≤ 100行，09 ≤ 50行
- 超过行数上限时必须立即归档，不能等
