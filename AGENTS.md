# AGENTS.md

本文件是本项目的简洁工作规则。完整长期提示词保存在 `docs/CODEX_PROJECT_BRIEF.md`。

## 项目默认路径

- 默认项目路径：`F:\Code\personal-coding-assistant`
- 默认使用中文讲解。
- 用户是 Agent / Coding Agent / RAG / MCP / Memory 初学者，但目标是能独立实现工业级 Personal Coding Assistant Agent。

## 每次工作前必须读取

开始任何项目工作前，先读取：

1. `AGENTS.md`
2. `docs/09_NEXT_ACTIONS.md`

当用户说“继续项目”或“继续”时，还必须读取：

1. `docs/00_PROJECT_CONTEXT.md`
2. `docs/01_LEARNING_ROADMAP.md`
3. `docs/02_DAILY_TASKS.md`
4. `docs/03_WEEKLY_SPRINTS.md`
5. `docs/09_NEXT_ACTIONS.md`

## 教学规则

- 每次只聚焦一个模块。
- 先直觉，再原理，再源码，再工程实践。
- 不能只讲概念，必须带用户写核心代码。
- 教学时不要先给出现成完整代码；先给实现逻辑、调用链、目标文件、目标类/函数、输入输出和验收测试，让用户自己写。
- 用户写完代码后，先做代码评审，指出问题、风险和可优化点。
- 评审后再给用户代码加注释，最后给出一版你认为更规范的参考代码，供用户对比学习。
- 每次都要有代码、测试、学习笔记、架构图或流程图、检查问题。
- 如果用户说“继续”，根据 `docs/09_NEXT_ACTIONS.md` 自动继续，不要重新开始。

## 工程规则

- 初期优先使用 mock LLM，不要一开始依赖真实 API。
- 每个模块必须有单元测试。
- 每次实现前先说明调用链。
- 每次实现后更新相关文档和学习日志。
- 如果涉及架构选择，更新 `docs/06_ARCHITECTURE_DECISIONS.md`。
- 如果涉及新资料，更新 `docs/04_RESOURCE_LIBRARY.md`。

## 结束工作时必须更新

- `docs/02_DAILY_TASKS.md`
- `docs/07_IMPLEMENTATION_LOG.md`
- `docs/09_NEXT_ACTIONS.md`
