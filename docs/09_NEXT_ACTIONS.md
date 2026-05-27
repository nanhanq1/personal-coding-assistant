# Next Actions

## 下次会话开始前必须读取

1. `AGENTS.md`
2. `docs/09_NEXT_ACTIONS.md`

如果用户说“继续项目”或“继续”，继续读取：

1. `docs/00_PROJECT_CONTEXT.md`
2. `docs/01_LEARNING_ROADMAP.md`
3. `docs/02_DAILY_TASKS.md`
4. `docs/03_WEEKLY_SPRINTS.md`
5. `docs/09_NEXT_ACTIONS.md`

## 当前进度

- 当前阶段：第 1 周 Agent Loop。
- 已完成：项目文档初始化、最小 Python 包结构、message schema、mock LLM、最小 Agent Loop、Agent Loop 测试、示例脚本回归测试。
- 已补充长期教学规则：后续不要先给出现成完整代码；先给逻辑、调用链、代码位置、测试目标和验收标准，让用户自己写；写完后先评审、再注释、再给规范参考代码用于对比。
- 当前阻塞：无。

## 下一次应该继续做什么

继续第 1 周 Day 2：Tool System 入门。

教学执行方式：先讲 Tool System 的直觉、原理和调用链，再给 `src/pca/tools/base.py`、`src/pca/tools/registry.py`、`tests/test_tools.py` 的实现目标和验收标准；不要直接给完整代码，等用户写完后进行代码评审、注释和参考实现对比。

建议任务：

1. 讲解 Tool 抽象解决什么问题。
2. 实现 `src/pca/tools/base.py` 的 `Tool` 数据结构。
3. 实现 `src/pca/tools/registry.py` 的 `ToolRegistry`。
4. 把 `AgentLoop` 从直接使用 `dict[str, callable]` 升级为使用 `ToolRegistry`。
5. 编写 `tests/test_tools.py`。
6. 更新学习笔记、实现日志和 next actions。
