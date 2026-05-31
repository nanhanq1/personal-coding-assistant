# Implementation Log

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
