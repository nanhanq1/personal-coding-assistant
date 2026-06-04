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

- 当前阶段：第 1 周 Day 3 文件工具已完成第一轮评审和补充，准备进入 Day 3 复盘与面试题回答。
- 已完成：项目文档初始化、最小 Python 包结构、message schema、mock LLM、最小 Agent Loop、Agent Loop 测试、示例脚本回归测试。
- 已完成 Day 1 学习验收：用户已经读懂代码，并能解释 Agent Loop、Message history、ToolCall、mock LLM 和 max_turns。
- 已修复 Day 1 遗留导入问题：核心模块和测试统一使用标准 `pca...` 导入。
- 已完成 Day 2 Tool System：实现 `Tool`、`ToolRegistry`、工具系统测试，并将 `AgentLoop` 从 `dict[str, callable]` 升级为使用 `ToolRegistry`。
- 已修复 Day 2 遗留问题：`ToolRegistry` 内部字段名统一为 `_tools`；`examples/01_minimal_agent.py` 先插入 `src` 路径再导入 `pca...`。
- 最新测试结果：`python -m pytest -q` 为 `8 passed, 1 warning`。
- 已补充长期教学规则：后续不要先给出现成完整代码；先给逻辑、调用链、代码位置、测试目标和验收标准，让用户自己写；写完后先评审、再注释、再给规范参考代码用于对比。
- 已补充长期代码规范：新增或修改代码中的注释默认使用中文。
- 已补充每日任务规则：后续每日任务必须包含资料推荐、所需前置知识、当天必须理解的知识点和网页版视频 / 课程页面。
- 已补充每日任务规则：后续每日任务必须包含面试题。
- 已补充代码评审后讲解规则：用户写完代码并完成评审、中文注释和参考实现对比后，必须指出当前代码处于项目整体的哪个阶段，以及它在整体架构、完整代码、安全性和容错性方面仍存在哪些问题。
- 已补充资料和视频推荐规则：后续资料推荐和视频推荐必须提供有效、正确、可访问链接，优先官方资料、GitHub、公开视频或课程页面；链接不确定时先验证再推荐。
- 已补充每日面试题归档规则：完成一天的任务和要求后，必须把当天面试题保存到 `docs/Compilation-of-Interview-Questions.md`，标题格式为“第几天 + 年月日”，内容包含面试题、用户回答和标准回答。
- 已补全第 1 天和第 2 天的面试题归档内容：第 1 天用户回答根据学习验收记录整理；第 2 天当前没有找到用户原回答记录，用户回答字段先标记为“待补充”。
- 已完成 2026-06-02 收尾复核：当前没有新增业务代码，测试仍然通过。
- 最新测试结果：`python -m pytest -q` 为 `8 passed, 1 warning in 0.16s`；warning 来自 `.pytest_cache` 写入权限，不影响功能验收。
- 已完成 Day 3 文件工具第一轮实现和评审：`read_file` / `write_file` 通过 `workspace_root` 限制读写范围。
- 已补充 `tests/test_file_tools.py`，覆盖读取、写入、空内容、缺少内容、空路径、路径越界和 `ToolRegistry` 集成。
- 最新测试结果：`python -m pytest tests\test_file_tools.py -q` 为 `8 passed`；`python -m pytest -q` 为 `16 passed`。
- 已新增 ADR-0003：文件工具必须限制在 `workspace_root` 内。
- 当前阻塞：无。

## 下一次应该继续做什么

继续第 1 周 Day 3：文件工具复盘与面试题回答。

教学执行方式：先复盘用户原实现中的问题，再讲补充后的 `workspace_root` 路径边界、`tmp_path` 测试方式和 `ToolRegistry` 集成链路。然后让用户回答 Day 3 面试题；完成回答后，把 Day 3 面试题、用户回答和标准回答保存到 `docs/Compilation-of-Interview-Questions.md`。之后再进入 Day 4 shell runtime。

建议任务：

1. 复盘 `read_file` / `write_file` 的调用链。
2. 解释为什么路径越界应抛 `ValueError`，文件不存在应抛 `FileNotFoundError`。
3. 解释为什么空字符串是合法文件内容。
4. 让用户回答 Day 3 面试题。
5. 将 Day 3 面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
6. 完成 Day 3 收尾后进入第 1 周 Day 4：shell runtime 雏形。

## 用户下次应发送的指令

```text
继续项目，完成第 1 周 Day 3：文件工具复盘和面试题归档，然后进入 Day 4：shell runtime 雏形。
```
