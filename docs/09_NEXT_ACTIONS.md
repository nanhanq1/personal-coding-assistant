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

- 已完成 GitHub 发布准备：补充公开版 `README.md`，补强 `.gitignore`，并准备配置远程仓库 `https://github.com/nanhanq1/personal-coding-assistant.git`。
- 当前阶段：第 1 周 Day 6 文档和架构图已完成，准备进入 Day 7：周复盘和小重构。
- 已完成：项目文档初始化、最小 Python 包结构、message schema、mock LLM、最小 Agent Loop、Agent Loop 测试、示例脚本回归测试。
- 已完成 Day 1 学习验收：用户已经读懂代码，并能解释 Agent Loop、Message history、ToolCall、mock LLM 和 max_turns。
- 已修复 Day 1 遗留导入问题：核心模块和测试统一使用标准 `pca...` 导入。
- 已完成 Day 2 Tool System：实现 `Tool`、`ToolRegistry`、工具系统测试，并将 `AgentLoop` 从 `dict[str, callable]` 升级为使用 `ToolRegistry`。
- 已修复 Day 2 遗留问题：`ToolRegistry` 内部字段名统一为 `_tools`；`examples/01_minimal_agent.py` 先插入 `src` 路径再导入 `pca...`。
- 最新测试结果：`python -m pytest -q` 为 `8 passed, 1 warning`。
- 已更新长期教学规则：后续先讲清代码逻辑、调用链、代码位置、输入输出、验收测试和安全边界，让被教学者真正理解；理解后给出完整、安全、全面、工程级代码。如果用户先写代码，则先评审、再中文注释、再给工程级参考代码用于对比。
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
- 已完成 Day 3 面试题回答评审，并将第 3 天记录追加到 `docs/Compilation-of-Interview-Questions.md`。
- 已补齐 `docs/05_LEARNING_NOTES.md` 的 Day 3 文件工具学习笔记、调用链、流程图、检查问题和工业级增强方向。
- 已完成 Day 4 shell runtime 第一轮实现和评审：命令执行通过 `workspace_root` 限制工作目录，并返回 `stdout`、`stderr`、`returncode` 和 `timed_out`。
- 已将 subprocess 执行逻辑拆到 `src/pca/runtime/shell_runtime.py` 的 `ShellRuntime`，`ShellCommandTool` 只负责工具包装和转发。
- 已补充 `tests/test_shell_runtime.py`，覆盖成功命令、失败命令、工作目录、超时、环境变量、输出捕获、runtime 层直接执行、`timeout_seconds` 规范化和 `ToolRegistry` 集成。
- 最新测试结果：`python -m pytest tests\test_file_tools.py tests\test_shell_runtime.py -q` 为 `37 passed, 1 skipped`；`python -m pytest -q` 为 `45 passed, 1 skipped`。
- 已新增并补充 ADR-0004：shell runtime 先实现受工作区限制的同步命令执行，且执行逻辑属于 runtime 层。
- 已完成 2026-06-06 工业级代码审查：移除正式源码硬编码 API key，Responses API 实验脚本改为环境变量和惰性 client，工具系统、消息结构、AgentLoop、文件工具和 shell runtime 均补充边界校验。
- 已创建修改前代码快照：`docs/code_reviews/2026-06-06-before-industrial-refactor/`；旧版 API key 已脱敏。
- 已在核心修改后的新源码中补充“修改前旧代码”注释片段，便于就地对比学习。
- 已新增 `tests/test_api_experiments.py`，防止正式源码再次出现硬编码 key。
- 已新增 ADR-0005：工业级加固必须先处理输入校验、错误回写和密钥边界。
- 最新测试结果：`python -m pytest -q` 为 `62 passed, 1 skipped`。
- 最新示例验证：`python examples\01_minimal_agent.py` 成功输出 `user -> assistant -> tool:echo -> assistant`。
- 最新编译验证：`python -m compileall src examples -q` 通过。
- 已完成 Day 4 shell runtime 复盘与面试题回答评审。
- 已将第 4 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- 已增强 shell runtime：`command` 现在支持 `list[str]`，列表命令使用 `shell=False`；字符串命令继续兼容 `shell=True`。
- 已开始 Day 5 Loop + Tools 整合：新增 `create_coding_tool_registry()`，统一注册 `ReadFileTool`、`WriteFileTool` 和 `ShellCommandTool`。
- 已新增 `tests/test_loop_tools_integration.py`，验证 `AgentLoop` 可以通过默认工具注册表连续执行 `write_file -> read_file -> final answer`。
- 最新测试结果：`python -m pytest tests\test_loop_tools_integration.py -q` 为 `1 passed`。
- 最新全量测试结果：`python -m pytest -q` 为 `66 passed, 1 skipped`。
- 最新示例验证：`python examples\01_minimal_agent.py` 成功输出 `user -> assistant -> tool:echo -> assistant`。
- 最新编译验证：`python -m compileall src examples -q` 通过。
- 已完成 Day 5 面试题回答评审。
- 已将第 5 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- 已完成 Day 6 文档和架构图：更新 `README.md`，新增 `docs/10_WEEK1_INTERVIEW_SCRIPT.md`，补充 `docs/05_LEARNING_NOTES.md` 的 Day 6 学习笔记。
- 已将第 6 天面试题追加到 `docs/Compilation-of-Interview-Questions.md`，用户回答先标记为“待补充”。
- 最新全量测试结果：`python -m pytest -q` 为 `66 passed, 1 skipped`。
- 最新示例验证：`python examples\01_minimal_agent.py` 成功输出 `user -> assistant -> tool:echo -> assistant`。
- 最新编译验证：`python -m compileall src examples -q` 通过。
- 当前阻塞：无。

## 下一次应该继续做什么

继续第 1 周 Day 7：周复盘和小重构。

教学执行方式：先带用户复盘第 1 周完整闭环，再检查现有代码是否有小而必要的重构点。重点不是大改架构，而是从测试覆盖、命名、边界校验、文档一致性和面试表达角度完成第 1 周收口。

建议任务：

1. 让用户回答 Day 6 面试题，并评审回答质量。
2. 对第 1 周代码做一次小范围复盘：`src/pca/core/`、`src/pca/tools/`、`src/pca/runtime/` 和 `tests/`。
3. 检查是否存在命名不一致、重复逻辑、测试缺口或文档与代码不一致。
4. 只做必要的小重构，避免提前引入 planner、权限系统或真实 LLM。
5. 运行 `python -m pytest -q`、`python examples\01_minimal_agent.py` 和 `python -m compileall src examples -q` 做 Day 7 验证。
6. 结束时更新 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

## 用户下次应发送的指令

```text
继续项目，开始第 1 周 Day 7：周复盘和小重构。请先评审我对 Day 6 面试题的回答。
```
