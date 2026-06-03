# Implementation Log

## 2026-06-03

### 本次完成

- 补全 `docs/Compilation-of-Interview-Questions.md` 中第 1 天和第 2 天的面试题归档内容。
- 第 1 天用户回答根据 2026-05-31 学习验收记录和记忆摘要整理，避免伪造逐字原文。
- 第 2 天当前没有找到用户面试题回答记录，因此用户回答字段标记为“待补充”。
- 同步更新 `docs/08_INTERVIEW_BANK.md`，增加 Tool System 面试题。
- 补充每日面试题归档规则：完成一天任务和要求后，必须把当天面试题保存到 `docs/Compilation-of-Interview-Questions.md`。
- 规定归档标题格式为“第几天 + 年月日”，内容包含面试题、用户回答和标准回答。
- 新增 `docs/Compilation-of-Interview-Questions.md`，作为每日面试题汇总文件。
- 同步更新 `AGENTS.md`、`docs/CODEX_PROJECT_BRIEF.md`、`docs/02_DAILY_TASKS.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 验证

- 本次只修改文档，未涉及业务代码。

## 2026-06-02

### 本次完成

- 完成第 1 周 Day 2 的收尾复核。
- 确认当前工作区在收尾前没有未提交变更。
- 运行项目测试，确认 Tool System、Agent Loop 集成和示例回归测试仍然通过。
- 更新收尾文档，明确下一次继续项目时进入第 1 周 Day 3：文件工具入门。

### 修改文件

- 更新 `docs/02_DAILY_TASKS.md`，补充 2026-06-02 收尾复核任务。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`，记录本次收尾、测试和修改文件。
- 更新 `docs/09_NEXT_ACTIONS.md`，刷新最新测试结果和下一次继续入口。

### 架构决策

- 本次没有新增架构决策。
- `docs/06_ARCHITECTURE_DECISIONS.md` 无需更新。

### 验证

- 运行 `python -m pytest -q`：`8 passed, 1 warning in 0.16s`。
- warning 来自 `.pytest_cache` 写入权限：`WinError 5`，不影响功能测试结果。

## 2026-06-01

### 本次完成

- 完成第 1 周 Day 2：Tool System 入门。
- 新增 `Tool` 抽象，用名称、描述和 handler 包装一个可执行工具。
- 新增 `ToolRegistry`，统一负责工具注册、查找、执行和错误处理。
- 将 `AgentLoop` 从直接使用 `dict[str, callable]` 升级为通过 `ToolRegistry.run(...)` 执行工具。
- 更新 `examples/01_minimal_agent.py`，让示例也走 `ToolRegistry`。
- 评审并修复两类问题：registry 内部字段名不一致、示例脚本导入顺序错误。

### 修改文件

- 修改 `src/pca/tools/base.py`，实现 `Tool`。
- 修改 `src/pca/tools/registry.py`，实现 `ToolRegistry`。
- 修改 `src/pca/core/agent_loop.py`，接入工具注册表。
- 修改 `tests/test_tools.py`，覆盖工具系统行为。
- 修改 `tests/test_agent_loop.py`，覆盖 Agent Loop 与 ToolRegistry 的集成。
- 修改 `examples/01_minimal_agent.py`，更新示例脚本的工具注册方式。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/06_ARCHITECTURE_DECISIONS.md`、`docs/07_IMPLEMENTATION_LOG.md`、`docs/09_NEXT_ACTIONS.md`。

### 架构决策

- 新增 ADR-0002：第 1 周 Day 2 使用 `ToolRegistry` 管理工具调用。

### 验证

- 运行 `python -m pytest -q`：`8 passed, 1 warning in 0.14s`。
- warning 来自 `.pytest_cache` 写入权限：`WinError 5`，不影响功能测试结果。

## 2026-05-31

### 本次完成

- 完成 Day 1 最小 Agent Loop 的学习验收。
- 评审用户对 5 个检查问题的回答。
- 确认用户已经理解 Agent Loop、Message history、ToolCall、mock LLM 和 max_turns 的核心作用。
- 确认下一步可以进入第 1 周 Day 2：Tool System 入门。
- 运行测试时发现 `src.pca...` 导入导致示例脚本无法从仓库根目录直接运行。
- 已将核心模块和测试中的导入统一回标准 `pca...` 形式。

### 修改文件

- 更新 `docs/02_DAILY_TASKS.md`，记录 Day 1 学习验收结果。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`，记录本次总结。
- 更新 `docs/09_NEXT_ACTIONS.md`，明确下一次继续项目的指令和任务。
- 修改 `src/pca/core/agent_loop.py`、`src/pca/core/mock_llm.py`、`tests/test_agent_loop.py`，修复导入路径。

### 架构决策

- 本次没有新增架构决策。
- `docs/06_ARCHITECTURE_DECISIONS.md` 无需更新。

### 验证

- 首次运行 `python -m pytest -q`：`1 failed, 1 passed`，失败原因是示例脚本执行时内部模块仍使用 `from src.pca...` 导入。
- 修复导入后再次运行 `python -m pytest -q`：`2 passed, 1 warning in 0.16s`。
- 运行 `python examples/01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。

## 2026-05-27

### 本次实现

- 更新 `AGENTS.md` 的教学规则：后续教学不先给出现成完整代码，而是先给实现逻辑、调用链、代码位置、输入输出和验收测试。
- 更新 `docs/CODEX_PROJECT_BRIEF.md` 的项目级长期教学提示词。
- 新增 Codex 记忆扩展说明，请求把该教学流程写入长期记忆。
- 补充长期代码注释规则：新增或修改代码中的注释默认使用中文。
- 补充每日任务生成规则：后续每日任务必须包含资料推荐、所需前置知识、当天必须理解的知识点和网页版视频 / 课程页面。
- 补充每日任务生成规则：后续每日任务必须包含面试题。
- 补充代码评审后讲解规则：用户完成代码、评审、注释和参考实现对比后，必须说明当前代码所处项目阶段，并指出它在整体架构、完整代码、安全性和容错性方面的不足。
- 补充资料和视频推荐规则：后续推荐资料和视频时必须提供有效、正确、可访问链接，优先官方资料、GitHub、公开视频或课程页面；链接不确定时先验证再推荐。

### 验证

- 本次只修改文档和记忆说明，未涉及业务代码。

## 2026-05-26

### 本次实现

- 初始化项目规则文件 `AGENTS.md`。
- 初始化长期提示词文件 `docs/CODEX_PROJECT_BRIEF.md`。
- 创建 `docs/00_PROJECT_CONTEXT.md` 到 `docs/09_NEXT_ACTIONS.md`。
- 创建 Python 项目结构 `src/pca/`、`tests/`、`examples/`。
- 用 TDD 先写 `tests/test_agent_loop.py`，观察到 `ModuleNotFoundError: No module named 'pca'`。
- 实现最小 message schema、mock LLM、Agent Loop。
- 运行示例时发现 `examples/01_minimal_agent.py` 找不到 `pca` 包；根因是 pytest 配置了 `src` 路径，但直接运行示例脚本没有。
- 新增 `tests/test_examples.py` 作为回归测试。
- 修复示例脚本，使它从仓库根目录直接运行时能加载 `src/pca`。

### 遇到的问题

- `rg` 在当前环境中执行被拒绝，后续使用 PowerShell 原生命令作为 fallback。

### 验证

- `python -m pytest -q`：`2 passed in 0.13s`。
- `python examples/01_minimal_agent.py`：输出 `user -> assistant -> tool:echo -> assistant`。
