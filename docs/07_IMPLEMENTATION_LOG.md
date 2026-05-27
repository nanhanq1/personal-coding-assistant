# Implementation Log

## 2026-05-27

### 本次实现

- 更新 `AGENTS.md` 的教学规则：后续教学不先给出现成完整代码，而是先给实现逻辑、调用链、代码位置、输入输出和验收测试。
- 更新 `docs/CODEX_PROJECT_BRIEF.md` 的项目级长期教学提示词。
- 新增 Codex 记忆扩展说明，请求把该教学流程写入长期记忆。
- 补充长期代码注释规则：新增或修改代码中的注释默认使用中文。

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
