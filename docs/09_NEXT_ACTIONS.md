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

- 当前阶段：第 1 周 Day 2 已完成，准备进入 Day 3 文件工具。
- 已完成：项目文档初始化、最小 Python 包结构、message schema、mock LLM、最小 Agent Loop、Agent Loop 测试、示例脚本回归测试。
- 已完成 Day 1 学习验收：用户已经读懂代码，并能解释 Agent Loop、Message history、ToolCall、mock LLM 和 max_turns。
- 已修复 Day 1 遗留导入问题：核心模块和测试统一使用标准 `pca...` 导入。
- 已完成 Day 2 Tool System：实现 `Tool`、`ToolRegistry`、工具系统测试，并将 `AgentLoop` 从 `dict[str, callable]` 升级为使用 `ToolRegistry`。
- 已修复 Day 2 遗留问题：`ToolRegistry` 内部字段名统一为 `_tools`；`examples/01_minimal_agent.py` 先插入 `src` 路径再导入 `pca...`。
- 最新测试结果：`python -m pytest -q` 为 `8 passed, 1 warning`。
- 已补充长期教学规则：后续不要先给出现成完整代码；先给逻辑、调用链、代码位置、测试目标和验收标准，让用户自己写；写完后先评审、再注释、再给规范参考代码用于对比。
- 已补充长期代码规范：新增或修改代码中的注释默认使用中文。
- 已补充每日任务规则：后续每日任务必须包含资料推荐、所需前置知识、当天必须理解的知识点和网页版视频 / 课程页面。
- 当前阻塞：无。

## 下一次应该继续做什么

继续第 1 周 Day 3：文件工具入门。

教学执行方式：先讲文件工具为什么是 Coding Agent 的第一类真实能力，再讲路径、workspace 边界、输入输出和失败场景；不要直接给完整代码，先给 `read_file` / `write_file` 的目标文件、函数签名、测试目标和验收标准，等用户写完后进行代码评审、中文注释和参考实现对比。每日任务中必须补充资料推荐、所需前置知识、当天必须理解的知识点和网页版视频 / 课程页面。

建议任务：

1. 讲解文件工具在 Coding Agent 中解决什么问题。
2. 设计 `read_file` 工具的输入输出和错误处理。
3. 设计 `write_file` 工具的输入输出和安全边界。
4. 在 `src/pca/tools/file_tools.py` 中实现最小文件工具。
5. 编写 `tests/test_file_tools.py`，覆盖读取、写入、文件不存在和路径边界。
6. 将文件工具注册进 `ToolRegistry` 的示例或测试中。
7. 更新学习笔记、实现日志和 next actions。

## 用户下次应发送的指令

```text
继续项目，开始第 1 周 Day 3：文件工具入门。请先讲直觉、原理、调用链、目标文件、输入输出和验收测试，不要直接给完整代码。
```
