# AGENTS.md

本文件是核心执行规则。详细标准见引用文件。

## 项目基础

- 默认路径：`F:\Code\personal-coding-assistant`
- 默认语言：中文
- 用户背景：大学生，目标是独立实现工业级 Personal Coding Assistant Agent

## 必读文件

开始工作前读取：`AGENTS.md`、`docs/INDEX.md`、`docs/09_NEXT_ACTIONS.md`

继续项目时追加读取：`docs/00_PROJECT_CONTEXT.md`、`docs/01_LEARNING_ROADMAP.md`、`docs/02_DAILY_TASKS.md`、`docs/03_WEEKLY_SPRINTS.md`

其他文件按 `docs/INDEX.md` 中的分类按需读取，不要一次性读取所有文档。

## 核心规则

### P0：必须遵守

- 每次只聚焦一个模块；默认中文讲解
- 用户说"继续"时，根据 `docs/09_NEXT_ACTIONS.md` 自动继续
- 代码注释默认中文；资料链接必须有效可访问
- 面试题未回答时不得归档，必须先推送用户回答
- 修改代码时必须保留"修改前旧代码"注释

### P1：教学流程

- 先直觉→原理→源码→工程实践；必须带用户写代码
- 先讲调用链、目标文件、输入输出、测试、安全边界，再给代码
- 出现流程/架构时必须给 Mermaid 图
- 用户先写代码时：先评审→补注释→给参考实现对比

### P2：每日产出

- 必须有代码、测试、笔记、面试题
- 任务必须含：前置知识、知识点、资料推荐、视频/课程链接
- 面试题归档格式：标题"第N天+日期"，含用户回答和标准回答

### P3：工业级加固

- 每2周实现后安排1周加固；加固周不新增模块
- 加固目标：把当前模块做到生产级质量，9个维度全部达标
- 详细标准见 `docs/INDUSTRIAL_STANDARDS.md`
- 核心要求：可观测性、健壮性、安全性、性能、可测试性、接口清晰、可扩展性、代码质量、真实验证
- 不达标不放行，宁可慢也不带半成品进入下一模块

### P4：面试题深度

- 每日三层次：概念理解、源码追查、系统设计
- 系统设计必须含深度追问：边界情况、优化思路、方案对比、如何测试

### P5：真实验证

- 模块完成后用真实代码库验证，不仅单元测试
- 用 Agent 修改真实小型项目，记录成功/失败/边界
- 验证结果记录到 `docs/07_IMPLEMENTATION_LOG.md`

## 外部技能调用

- 普通解释/状态/评审/答疑：不主动调用 skill
- 代码实现/调试/验收/复杂设计：按需使用 TDD、调试、验证流程

## 工程规则

- 初期用 mock LLM，不依赖真实 API
- 每个模块必须有单元测试
- 实现前先说明调用链，实现后更新文档
- 架构选择更新 `docs/06_ARCHITECTURE_DECISIONS.md`
- 新资料更新 `docs/04_RESOURCE_LIBRARY.md`

## 工作结束时必须更新

- `docs/02_DAILY_TASKS.md`
- `docs/07_IMPLEMENTATION_LOG.md`
- `docs/09_NEXT_ACTIONS.md`
