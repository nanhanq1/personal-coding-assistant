# Implementation Log

## 2026-06-08

### 本次完成

- 进行第 1 周 Day 7：周复盘和小重构。
- 复盘当前核心链路：`AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler/runtime`。
- 确认 Day 7 不做大架构调整，不提前引入 planner、权限系统或真实 LLM。
- 运行 Day 7 初始基线验证，确认第 1 周代码在重构前稳定。
- 按 TDD 新增文件工具边界测试：`path` 必须是字符串，不能把数字等坏参数静默转成文件名。
- 修复 `src/pca/tools/file_tools.py` 的 `_resolve_workspace_path(...)`，明确拒绝非字符串 `path`。
- 更新 `README.md`、`docs/02_DAILY_TASKS.md`、`docs/04_RESOURCE_LIBRARY.md`、`docs/05_LEARNING_NOTES.md`、`docs/Compilation-of-Interview-Questions.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 架构决策

- 本次没有新增 ADR。
- Day 7 只是第 1 周收口型小重构，继续沿用已有工具路由和 workspace 边界设计。

### 验证

- 初始基线运行 `python -m pytest -q`：`66 passed, 1 skipped`。
- 初始基线运行 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 初始基线运行 `python -m compileall src examples -q`：通过。
- RED：运行 `python -m pytest tests\test_file_tools.py -q`，新增两个非字符串路径测试失败，证明 `path=123` 会被错误处理。
- GREEN：修复后运行 `python -m pytest tests\test_file_tools.py -q`：`25 passed, 1 skipped`。
- 全量验证运行 `python -m pytest -q`：`68 passed, 1 skipped`。

## 2026-06-08

### 本次完成

- 继续第 1 周 Day 6：文档和架构图。
- 复盘第 1 周 Day 1 到 Day 5 已完成能力：`Message` / `ToolCall`、`ScriptedLLM`、`AgentLoop`、`ToolRegistry`、文件工具、shell runtime 和默认 coding 工具注册表。
- 更新 `README.md`，补齐当前能力、Agent 执行闭环图、工具路由链路图、运行方式、测试方式和面试讲解要点。
- 新增 `docs/10_WEEK1_INTERVIEW_SCRIPT.md`，沉淀第 1 周面试讲解稿初稿。
- 更新 `docs/05_LEARNING_NOTES.md`，新增 Day 6 文档和架构图学习笔记。
- 更新 `docs/04_RESOURCE_LIBRARY.md`，补充 Day 6 资料链接。
- 将第 6 天面试题追加到 `docs/Compilation-of-Interview-Questions.md`，用户回答先标记为“待补充”。
- 更新 `docs/02_DAILY_TASKS.md` 和 `docs/09_NEXT_ACTIONS.md`，准备推进到 Day 7 周复盘和小重构。

### 架构决策

- 本次没有新增架构决策。
- Day 6 是对既有 Agent Loop 和 Tool Routing 闭环的文档化，不改变源码边界。

### 验证

- 运行 `python -m pytest -q`：`66 passed, 1 skipped`。
- 运行 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 运行 `python -m compileall src examples -q`：通过。

## 2026-06-08

### 本次完成

- 开始第 1 周 Day 5：整合 Loop + Tools。
- 按 TDD 新增 `tests/test_loop_tools_integration.py`，先观察 RED：`pca.tools` 中缺少 `create_coding_tool_registry`。
- 在 `src/pca/tools/__init__.py` 中新增 `create_coding_tool_registry()`。
- 默认注册表统一注册 `ReadFileTool`、`WriteFileTool` 和 `ShellCommandTool`。
- 通过集成测试验证 `AgentLoop` 可以连续路由 `write_file` 和 `read_file`，并把每次工具结果写回 `message history`。
- 评审用户对 Day 5 Loop + Tools 整合面试题的回答。
- 将第 5 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/04_RESOURCE_LIBRARY.md`、`docs/05_LEARNING_NOTES.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 架构决策

- 本次没有新增架构决策。
- 继续沿用已有链路：`AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler/runtime`。
- `create_coding_tool_registry()` 只是内置工具组合入口，不改变 AgentLoop、权限系统或 runtime 边界。

### 验证

- 先运行 `python -m pytest tests\test_loop_tools_integration.py -q` 观察 RED：失败原因为 `cannot import name 'create_coding_tool_registry' from 'pca.tools'`。
- 实现默认工具注册表后运行 `python -m pytest tests\test_loop_tools_integration.py -q`：`1 passed`。
- 运行 `python -m pytest -q`：`66 passed, 1 skipped`。
- 运行 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 运行 `python -m compileall src examples -q`：通过。

## 2026-06-07

### 本次完成

- 补充公开发布用 `README.md`，说明项目目标、当前能力、目录结构、运行方式、测试方式、设计原则和学习路线。
- 补强 `.gitignore`，覆盖 Python 缓存、测试缓存、虚拟环境、构建产物、环境变量、IDE 配置、本地临时目录、日志、数据库文件和系统文件。
- 准备将仓库发布到 GitHub：`https://github.com/nanhanq1/personal-coding-assistant.git`。

### 验证

- 运行 `python -m pytest -q`：`65 passed, 1 skipped`。
- 已确认 `.idea/`、`.tmp/`、`.pytest_cache/` 和 `__pycache__/` 仅作为 ignored 本地文件存在，不进入 Git 索引。

## 2026-06-07

### 本次完成

- 增强 shell runtime 的 `command` 参数，支持官方推荐的 `list[str]` 形式。
- 字符串命令继续走 `shell=True`，保持早期用法兼容。
- 列表命令走 `shell=False`，避免手写 shell 引号和转义，减少参数解析歧义和 shell 注入风险。
- 新增测试覆盖列表命令执行、带空格参数传递和非法列表拒绝。
- 完成第 1 周 Day 4 shell runtime 复盘与面试题回答评审。
- 评审用户对 shell runtime 风险、`cwd` / `workspace_root`、输出字段、tool/runtime 分层和安全缺口的理解。
- 将第 4 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- 更新 `docs/02_DAILY_TASKS.md` 和 `docs/09_NEXT_ACTIONS.md`，把下一步推进到第 1 周 Day 5：整合 Loop + Tools。

### 验证

- 先运行 `python -m pytest tests\test_shell_runtime.py -q` 观察 RED：列表命令测试失败，原因是 `_require_command` 只允许字符串。
- 实现列表命令后运行 `python -m pytest tests\test_shell_runtime.py -q`：`24 passed`。

## 2026-06-06

### 本次完成

- 完成当前所有已实现代码的工业级审查，覆盖 `src/`、`tests/` 和 `examples/`。
- 创建修改前代码快照：`docs/code_reviews/2026-06-06-before-industrial-refactor/`，用于后续对比；旧版硬编码 API key 已在快照中脱敏。
- 发现并修复早期 Responses API 实验脚本中的硬编码 API key 问题。
- 将 `src/pca/response_test.py` 和 `src/pca/mini_LLM_01.py` 改为惰性创建 OpenAI client，只从 `PCA_OPENAI_API_KEY` 或 `OPENAI_API_KEY` 环境变量读取密钥。
- 修复早期实验脚本导入时依赖 OpenAI SDK 和真实 client 的问题，避免污染正式包导入路径。
- 新增 `tests/test_api_experiments.py`，扫描正式源码防止硬编码 key 回归。
- 为 `Tool` 增加名称、描述、handler 和 arguments 校验。
- 为 `ToolRegistry` 增加注册对象类型、工具名和 arguments 校验。
- 为 `ToolCall`、`Message` 和 `ScriptedLLM` 增加结构校验。
- 为 `AgentLoop` 增加 `llm`、`tools`、`max_turns` 和 `user_input` 校验。
- 调整 `AgentLoop` 工具错误处理：工具失败时把错误写回 `message history`，让 LLM 有机会恢复。
- 为文件工具补充 `workspace_root` 必须存在、读取目录错误稳定化、写入内容必须为字符串等边界。
- 为 shell runtime 补充 `workspace_root` / `cwd` 必须存在、超时上限、空环境变量名拒绝和 `duration_ms` 返回字段。
- 将源码占位模块和示例文件的说明文字改为中文。
- 新增 ADR-0005：工业级加固必须先处理输入校验、错误回写和密钥边界。
- 更新 `docs/05_LEARNING_NOTES.md`，补充本次工业级代码审查学习笔记。
- 按用户要求，在核心修改后的新源码中补充“修改前旧代码”注释片段，用于和当前实现就地对比；涉及敏感 API key 的旧代码片段已脱敏。
- 更新长期教学要求：把“不能直接给代码 / 必须先让用户自己写”调整为“先讲清代码逻辑并确认理解，再给出完整、安全、全面、工程级代码”。
- 同步更新 `AGENTS.md`、`docs/CODEX_PROJECT_BRIEF.md`、`docs/02_DAILY_TASKS.md` 和 `docs/09_NEXT_ACTIONS.md`。
- 评审用户重新修改的文件工具和 shell runtime 代码。
- 修复 `ReadFileTool`、`WriteFileTool`、`ShellCommandTool` 继承 `Tool` 后缺少 `handler` 的初始化问题。
- 修复 `write_file` 缺少 `content` 时的异常语义。
- 修复 shell runtime 的 `cwd` 解析，让相对路径以 `workspace_root` 为基准。
- 修复 Windows 下子进程输出中文路径时的解码问题，改用本机 locale。
- 调整文件工具测试中的平台假设：符号链接无权限时跳过，`..` 路径测试保持在工作区内。
- 新增并修复 `tests/test_shell_runtime.py`，覆盖命令成功、失败、工作目录、超时、环境变量、输出捕获和 `ToolRegistry` 集成。
- 根据代码评审发现的问题，将 shell 执行逻辑从 `src/pca/tools/shell_tools.py` 拆分到 `src/pca/runtime/shell_runtime.py`。
- 新增 `ShellRuntime`，由 runtime 层负责参数校验、`cwd` 解析、环境变量合并、`subprocess.run(...)` 调用和超时结果封装。
- 简化 `ShellCommandTool`，让它只负责注册 `run_command` 工具并转发给 runtime。
- 修复 `timeout_seconds` 字符串数字会传入 `subprocess.run(...)` 触发 TypeError 的问题，统一规范化为正浮点数。
- 保留命令自身失败的 `returncode`，但让工具参数错误直接抛 `ValueError`。
- 将 `tests/test_shell_runtime.py` 中的 Python 子进程命令改为使用 `sys.executable`，减少 PATH 依赖。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/04_RESOURCE_LIBRARY.md`、`docs/06_ARCHITECTURE_DECISIONS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 架构决策

- 新增 ADR-0005：工业级加固必须先处理输入校验、错误回写和密钥边界。
- 新增 ADR-0004：第 1 周 Day 4 shell runtime 先实现受工作区限制的同步命令执行。
- 更新 ADR-0003：`write_file` 写入嵌套路径时会自动创建缺失的父目录。
- 补充 ADR-0004：shell 执行逻辑属于 runtime 层，tool 层只负责包装和转发。

### 验证

- 先运行新增目标测试观察 RED：`python -m pytest tests\test_tools.py tests\test_agent_loop.py tests\test_file_tools.py tests\test_shell_runtime.py tests\test_api_experiments.py -q`，结果为 `17 failed, 44 passed, 1 skipped`。
- 修复后运行同一目标测试：`61 passed, 1 skipped`。
- 运行最新全量测试：`python -m pytest -q`，结果为 `62 passed, 1 skipped`。
- 运行 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 运行 `python -m compileall src examples -q`：通过。
- 扫描 `src/` 和修改前快照中的 `sk-` 字面量：未发现匹配。
- 先运行 `python -m pytest tests\test_shell_runtime.py -q` 观察 RED：失败原因为 `pca.runtime.shell_runtime` 中尚无 `run_command`。
- 拆分实现后运行 `python -m pytest tests\test_shell_runtime.py -q`：`17 passed`。
- 运行 `python -m pytest tests\test_file_tools.py tests\test_shell_runtime.py -q`：`37 passed, 1 skipped`。
- 运行 `python -m pytest -q`：`45 passed, 1 skipped`。

## 2026-06-05

### 本次完成

- 补齐 `docs/05_LEARNING_NOTES.md` 的 Day 3 文件工具学习笔记、调用链、流程图、检查问题和工业级增强方向。
- 评审用户对 Day 3 文件工具四个面试题的回答。
- 将第 3 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- 明确补充点：message history 可用于复盘和重新推理，但完整回滚需要 checkpoint、git diff 或 workspace snapshot。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`，把项目推进到 Day 4 shell runtime。

### 验证

- 运行 `python -m pytest -q`：`16 passed`。

## 2026-06-04

### 本次完成

- 评审用户实现的 Day 3 文件工具代码和测试。
- 修复 `read_file` / `write_file` 的类型标注、路径校验、编码和异常语义。
- 新增 `_resolve_workspace_path(...)`，把工具参数中的路径解析到 `workspace_root` 内。
- 将路径越界从“文件不存在时碰巧失败”改为明确抛出 `ValueError`。
- 允许 `write_file` 写入空字符串，避免把合法空文件内容误判为缺少内容。
- 重写 `tests/test_file_tools.py`，覆盖文件读写、空内容、缺少内容、空路径、路径越界和 `ToolRegistry` 集成。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/04_RESOURCE_LIBRARY.md`、`docs/06_ARCHITECTURE_DECISIONS.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 修改文件

- 修改 `src/pca/tools/file_tools.py`，实现 Day 3 文件工具。
- 修改 `tests/test_file_tools.py`，补全文件工具测试。
- 更新 `docs/02_DAILY_TASKS.md`，记录 Day 3 当前进度。
- 更新 `docs/04_RESOURCE_LIBRARY.md`，补充文件工具相关资料链接。
- 更新 `docs/06_ARCHITECTURE_DECISIONS.md`，新增 ADR-0003。
- 更新 `docs/07_IMPLEMENTATION_LOG.md`，记录本次评审和补充。
- 更新 `docs/09_NEXT_ACTIONS.md`，刷新下一步任务。

### 架构决策

- 新增 ADR-0003：第 1 周 Day 3 文件工具必须限制在 `workspace_root` 内。

### 验证

- 运行 `python -m pytest tests\test_file_tools.py -q`：`8 passed in 0.09s`。
- 运行 `python -m pytest -q`：`16 passed in 0.22s`。

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
