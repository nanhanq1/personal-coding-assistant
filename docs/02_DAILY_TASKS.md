# Daily Tasks

## 2026-06-11

日期：2026-06-11
当前阶段：第 2 周 Day 3
当前模块：`edit_file` 局部编辑雏形
预计用时：60 分钟

### 1. 今日学习目标

- 理解局部编辑为什么比整文件覆盖更适合 Coding Agent 的小范围改动。
- 区分 `write_file` 和 `edit_file` 的使用边界。
- 按 TDD 新增 `edit_file` 行为测试，先观察 RED，再实现 GREEN。
- 实现只替换一次、且 `old_text` 必须唯一出现的最小 `EditFileTool`。
- 将 `edit_file` 注册到默认 coding 工具注册表，并让 schema 示例同步包含它。

### 2. 所需前置知识

- 第 1 周文件工具：`_resolve_workspace_path(...)` 如何限制 `workspace_root`。
- 第 2 周 Day 1：`ToolParameter`、`Tool.run(...)` 和工具参数 schema。
- 第 2 周 Day 2：`create_coding_tool_registry().list_tool_schemas()` 是未来 adapter 的工具清单来源。
- Python 字符串的 `count(...)`、`replace(..., 1)` 和文件读写。

### 3. 今日必须理解的知识点

- `write_file` 适合新建文件或整文件覆盖；`edit_file` 适合对已有文件的一段明确文本做小范围替换。
- `old_text` 必须非空，否则空字符串会匹配字符之间的所有位置，可能造成灾难性插入。
- `old_text` 必须唯一出现；如果出现多次，工具无法知道 LLM 想改哪一个语义位置。
- 工具参数 schema 只能说明参数形状，仍需要具体工具校验唯一匹配、路径边界和写入安全。
- Day 3 只做最小精确替换，不提前实现 diff/patch、追加模式、模糊匹配或 planner。

### 4. 今日代码 / 文档任务

- 在 `tests/test_file_tools.py` 中新增 `EditFileTool` RED 测试：成功替换、目标文本不存在、目标文本出现多次、空 `old_text`、非字符串 `new_text`、路径越界、函数形式和默认注册表集成。
- 在 `tests/test_tools.py` 中补充默认 coding 工具 schema 断言，要求 `edit_file` 暴露 `path`、`old_text`、`new_text`。
- 在 `src/pca/tools/file_tools.py` 中实现 `EditFileTool` 和函数形式 `edit_file(...)`。
- 在 `src/pca/tools/__init__.py` 中导出并注册 `EditFileTool`。
- 在 `tests/test_examples.py` 中同步 schema 示例断言，让默认工具列表包含 `edit_file`。
- 更新学习笔记、资料库、实现日志、下一步行动和每日面试题归档。

### 5. 今日资料推荐

- Python `difflib` 官方文档：https://docs.python.org/3/library/difflib.html
- GNU diffutils `patch` 手册：https://www.gnu.org/software/diffutils/manual/html_node/Merging-with-patch.html
- Real Python `pathlib` 教程：https://realpython.com/python-pathlib/

### 6. 今日输出物

- `EditFileTool`
- `edit_file(arguments: dict[str, Any]) -> str`
- 默认 coding 工具注册表中的 `edit_file`
- `edit_file` 参数 schema
- Day 3 局部编辑学习笔记
- 第 11 天面试题归档

### 7. 当前完成情况

- 已评审用户 3 个检查问题：用户已理解多处替换会导致语义错误，`old_text` 为空必须拦截，`edit_file` 和 `write_file` 的边界基本正确。
- 已按 TDD 写 RED 测试，初始运行 `pytest tests\test_file_tools.py -q` 时 8 个新增测试失败，原因是 `EditFileTool`、`edit_file` 函数和默认注册表中尚不存在 `edit_file`。
- 已实现 `EditFileTool`：复用 `_resolve_workspace_path(...)`，读取文件，要求 `old_text` 非空且唯一出现，然后用 `replace(old_text, new_text, 1)` 写回。
- 已将 `EditFileTool` 注册进 `create_coding_tool_registry()`。
- 已同步 `tests/test_tools.py` 和 `tests/test_examples.py`，让 schema 测试和示例测试反映新增的 `edit_file`。
- 已验证 `pytest tests\test_file_tools.py -q`：`33 passed, 1 skipped`。
- 已验证 `pytest tests\test_tools.py -q`：`16 passed`。
- 已验证 `pytest tests\test_file_tools.py tests\test_tools.py tests\test_examples.py -q`：`51 passed, 1 skipped`。
- 已验证 `pytest -q`：`84 passed, 1 skipped`。
- 已验证 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 已验证 `python examples\02_tool_agent.py`：成功输出包含 `read_file`、`write_file`、`edit_file`、`run_command` 的 schema JSON。
- 已验证 `python -m compileall src examples -q`：通过。
- Day 3 验收通过，下一步进入第 2 周 Day 4：结构化 tool result。

## 2026-06-11

日期：2026-06-11
当前阶段：第 2 周 Day 2
当前模块：默认工具 schema 展示示例与内置工具描述质量
预计用时：45 分钟

### 1. 今日学习目标

- 评审用户对 Day 2 三个检查问题的回答。
- 理解 `ToolRegistry` 是工具 schema 的唯一事实源，adapter 只做格式转换。
- 用 TDD 补充默认 coding 工具注册表的 schema 展示示例。
- 让 `examples/02_tool_agent.py` 输出 `create_coding_tool_registry().list_tool_schemas()` 的 JSON，作为未来 adapter 消费 schema 的教学样例。
- 优化内置工具描述质量，让模型能区分只读、写入覆盖和命令执行三类工具。

### 2. 所需前置知识

- `create_coding_tool_registry()` 会注册 `read_file`、`write_file`、`run_command`。
- `ToolRegistry.list_tool_schemas()` 会导出已注册工具的内部中立 schema。
- OpenAI / Anthropic adapter 后续应从内部 schema 转换格式，而不是重新手写工具清单。
- 当前仍使用 mock / 示例 / 测试，不接真实 API。

### 3. 今日必须理解的知识点

- 工具系统的事实源是 registry，不是某个 adapter。
- adapter 的职责是把内部 schema 改写成外部 API 格式，不负责决定项目有哪些工具。
- 示例脚本也要有测试，否则未来重构时很容易变成过期展示。
- `additionalProperties: True` 是当前项目宽松 schema 阶段的真实表达；严格模式属于后续 adapter/schema hardening。
- 工具描述不只是给人看的注释，也是模型选工具时的重要上下文；描述必须讲清用途、副作用、安全边界和返回值。

### 4. 今日代码 / 文档任务

- 在 `tests/test_examples.py` 中新增 RED 测试，要求 `examples/02_tool_agent.py` 输出可解析的默认工具 schema JSON。
- 将 `examples/02_tool_agent.py` 从占位文件改成 schema 展示示例。
- 在 `tests/test_tools.py` 中新增 RED 测试，要求内置工具 schema 描述包含用途、边界、副作用和返回语义。
- 优化 `ReadFileTool`、`WriteFileTool` 和 `ShellCommandTool` 的工具描述和参数描述。
- 修复 `examples/02_tool_agent.py` 在 Windows 子进程测试中 stdout 编码不稳定的问题。
- 将用户 Day 2 检查题回答归档到 `docs/Compilation-of-Interview-Questions.md`。
- 更新学习日志和下一步行动。

### 5. 今日资料推荐

- OpenAI Function calling / tool calling guide：https://developers.openai.com/api/docs/guides/function-calling
- OpenAI Using tools guide：https://developers.openai.com/api/docs/guides/tools
- Anthropic Define tools：https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- JSON Schema object 参考：https://json-schema.org/understanding-json-schema/reference/object

### 6. 今日输出物

- `tests/test_examples.py` 中的 schema 示例回归测试。
- `examples/02_tool_agent.py` 默认工具 schema 展示示例。
- 第 9 天面试题归档。

### 7. 当前完成情况

- 已评审用户 3 个检查问题：核心方向正确，需要补强“registry 是唯一事实源，adapter 是格式转换层”的表达。
- 已按 TDD 写 RED 测试，失败原因为 `examples/02_tool_agent.py` 没有输出 JSON。
- 已实现 `examples/02_tool_agent.py`，输出默认 coding 工具注册表的 schema JSON。
- 已验证 `pytest tests\test_examples.py -q`：`2 passed`。
- 已验证 `pytest tests\test_tools.py tests\test_examples.py -q`：`17 passed`。
- 已验证 `pytest -q`：`75 passed, 1 skipped`。
- 已验证 `python examples\02_tool_agent.py`：成功输出 `read_file`、`write_file`、`run_command` 的 schema JSON。
- 已验证 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 已验证 `python -m compileall src examples -q`：通过。
- 已按 TDD 新增工具描述质量 RED 测试，初始失败原因为 `read_file` 描述没有明确“只读取、不修改文件、返回文件文本”等模型选择边界。
- 已优化 `read_file`、`write_file`、`run_command` 的工具描述和参数描述。
- 已修复 `examples/02_tool_agent.py` 的 stdout UTF-8 编码设置，避免 Windows 子进程测试解码失败。
- 已验证 `pytest tests\test_tools.py -q`：`16 passed`。
- 已验证 `pytest tests\test_tools.py tests\test_examples.py -q`：`18 passed`。
- 已验证 `pytest -q`：`76 passed, 1 skipped`。
- 已验证 `python examples\02_tool_agent.py`：成功输出增强后的 schema JSON。
- 已验证 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 已验证 `python -m compileall src examples -q`：通过。
- 已评审用户对工具描述质量 3 个检查题的回答：前两题通过，第 3 题已补强“返回字段也是 LLM 调用前和调用后的契约”。
- 已将第 10 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- Day 2 验收通过，下一步进入第 2 周 Day 3：`edit_file` 局部编辑雏形。
- Day 2 收尾复核已重新运行：`pytest -q` 为 `76 passed, 1 skipped`；`python examples\02_tool_agent.py`、`python examples\01_minimal_agent.py` 和 `python -m compileall src examples -q` 均通过。
- 已补充项目级外部技能调用规则：普通解释、状态说明、面试题评审和文档答疑不主动调用额外 Superpowers skill；代码实现、调试、验收和复杂设计场景再按需调用。
- 已更新 `README.md`，将 GitHub 项目说明同步到第 2 周 Day 2 已完成状态，补充工具 schema 能力、schema 示例和最新验证基线。
- GitHub 同步前验证已重新运行：`pytest -q` 为 `76 passed, 1 skipped`；`python examples\01_minimal_agent.py`、`python examples\02_tool_agent.py` 和 `python -m compileall src examples -q` 均通过。
- 已提交并推送到 GitHub `origin/main`：`2aae93e docs: update README for tool schema progress`。

## 2026-06-10

日期：2026-06-10
当前阶段：第 2 周 Day 2 启动
当前模块：工具参数 schema 如何服务真实 LLM adapter
预计用时：60 分钟

### 1. 今日学习目标

- 审查第 2 周 Day 1 工具 schema 是否真正完成，不能只相信文档记录。
- 理解 `ToolRegistry.list_tool_schemas()` 为什么是未来 LLM adapter 的工具列表来源。
- 理解同一份内部 schema 在不同模型厂商中会被转换成不同外部格式。
- 理解工具名称、工具描述、参数描述和错误语义如何影响模型选工具。
- 准备为默认 coding 工具注册表补充 schema 展示示例或测试。

### 2. 所需前置知识

- 第 2 周 Day 1：`ToolParameter`、`Tool.to_schema()`、`ToolRegistry.list_tool_schemas()`。
- 第 1 周主链路：`AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler/runtime`。
- JSON Schema 中 `properties`、`required`、`additionalProperties` 的基础含义。
- OpenAI / Anthropic tool calling 都需要把工具名、描述和参数 schema 提供给模型。

### 3. 今日必须理解的知识点

- `list_tool_schemas()` 不是给人看的文档函数，而是未来 adapter 拼接 `tools` 参数的输入来源。
- 内部 schema 不应该直接绑定某一家 API；更稳妥的边界是先有项目内部中立格式，再由 adapter 转成 OpenAI / Anthropic 等格式。
- Day 1 当前决策是“不关闭 `additionalProperties`”，因为项目还没有实现完整 JSON Schema 严格模式，也还没有 adapter 层的格式转换。
- OpenAI strict tool schema 和当前项目 Day 1 schema 不是同一成熟度：OpenAI strict 模式要求对象内 `additionalProperties: false` 且字段都列为 required；当前项目先保留宽松 schema，避免假装已经具备严格模式。
- 工具描述质量会直接影响模型是否选对工具；描述太短、参数含义不清、返回值不明，都会提高错误 tool call 的概率。

### 4. 今日代码 / 文档任务

- 先完成 Day 1 完成度审查：跑 schema 目标测试、相关工具链测试、全量测试、示例和编译。
- 修复 Day 1 审查发现的 schema 契约漂移：`Tool.to_schema()` 必须与 ADR-0006 和测试一致。
- 讲清 Day 2 调用链、目标文件、目标函数、输入输出、验收测试和安全边界。
- 用户确认理解后，再按 TDD 为默认 coding 工具注册表补充 adapter-facing schema 展示示例或测试。
- 结束时继续更新 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 5. 今日资料推荐

- OpenAI Function calling / tool calling guide：https://developers.openai.com/api/docs/guides/function-calling
- OpenAI Using tools guide：https://developers.openai.com/api/docs/guides/tools
- Anthropic Tool use overview：https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Anthropic Define tools：https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- JSON Schema object 参考：https://json-schema.org/understanding-json-schema/reference/object

### 6. 今日输出物

- Day 1 完成度审查结论和修复。
- Day 2 调用链和设计边界。
- Day 2 学习笔记初稿。
- 下一步 TDD 实现入口。

### 7. 当前完成情况

- 已发现 Day 1 当前 checkout 存在 schema 契约漂移：实现导出 `additionalProperties: False`，但 ADR-0006 和测试期望暂不关闭。
- 已修复 `src/pca/tools/base.py`，让 `Tool.to_schema()` 导出 `additionalProperties: True`。
- 已验证 `pytest tests\test_tools.py -q`：`15 passed`。
- 已验证 `pytest tests\test_tools.py tests\test_file_tools.py tests\test_shell_runtime.py tests\test_loop_tools_integration.py -q`：`65 passed, 1 skipped`。
- 已验证 `pytest -q`：`74 passed, 1 skipped`。
- 已验证 `python examples\01_minimal_agent.py`：成功输出 `user -> assistant -> tool:echo -> assistant`。
- 已验证 `python -m compileall src examples -q`：通过。
- 已开始 Day 2 教学设计；尚未进入 Day 2 新生产代码实现，等待用户确认理解后按 TDD 继续。

## 2026-06-09

日期：2026-06-09
当前阶段：第 2 周 Day 1
当前模块：Tool System 深化：工具参数 schema
预计用时：60 分钟

### 1. 今日学习目标

- 理解工具 schema 为什么是 LLM 和程序之间的调用契约。
- 区分 schema 的基础参数校验和具体工具的业务安全校验。
- 实现 `ToolParameter`，让工具能声明参数名、JSON 类型、描述和是否必填。
- 实现 `Tool.to_schema()` 和 `ToolRegistry.list_tool_schemas()`。
- 给内置 `read_file`、`write_file` 和 `run_command` 声明参数 schema。

### 2. 所需前置知识

- 第 1 周主链路：`AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler/runtime`。
- Python `dataclass`、tuple、dict 和类型判断。
- JSON Schema 中的 `type`、`properties`、`required` 和 `additionalProperties`。
- 工具参数来自 LLM 输出，不能默认可信。

### 3. 今日必须理解的知识点

- `Tool schema` 是给 LLM adapter 和工具系统看的调用契约，不是真正执行工具的代码。
- schema 可以声明“需要哪些参数”和“参数大致是什么类型”。
- schema 不能替代业务安全校验，例如 `workspace_root` 越界检查、危险命令审批和文件覆盖策略。
- `Tool.run(...)` 是统一入口，适合放通用参数校验。
- 具体工具仍必须保留自己的语义校验和安全边界。

### 4. 今日代码 / 文档任务

- 在 `tests/test_tools.py` 中按 TDD 新增工具 schema、必填参数、类型校验和内置工具 schema 测试。
- 在 `src/pca/tools/base.py` 中新增 `ToolParameter`、`Tool.parameters` 和 `Tool.to_schema()`。
- 在 `src/pca/tools/registry.py` 中新增 `list_tool_schemas()`。
- 在文件工具和 shell 工具中声明参数 schema。
- 更新第 2 周 Sprint、学习笔记、资源库、实现日志、下一步行动和每日面试题归档。

### 5. 今日资料推荐

- JSON Schema object 参考：https://json-schema.org/understanding-json-schema/reference/object
- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling
- Python `dataclasses` 官方文档：https://docs.python.org/3/library/dataclasses.html

### 6. 今日输出物

- `ToolParameter`
- `Tool.to_schema()`
- `ToolRegistry.list_tool_schemas()`
- 内置工具参数 schema
- 第 2 周 Sprint
- Day 1 工具 schema 学习笔记

### 7. 完成情况

- 已评审今日检查问题：用户已能说明 schema 主要负责参数说明、必填字段和基础类型约束，不能替代路径边界、命令安全等逻辑校验。
- 已按 TDD 新增 schema 相关 RED 测试，初始失败原因为 `ToolParameter` 尚不存在。
- 已实现 `ToolParameter`、`Tool.to_schema()` 和 `ToolRegistry.list_tool_schemas()`。
- 已给 `read_file`、`write_file` 和 `run_command` 声明参数 schema。
- 已验证 `python -m pytest tests\test_tools.py -q` 为 `15 passed`。
- 已验证 `python -m pytest tests\test_tools.py tests\test_file_tools.py tests\test_shell_runtime.py tests\test_loop_tools_integration.py -q` 为 `65 passed, 1 skipped`。

## 2026-06-09

日期：2026-06-09
当前阶段：第 1 周 Day 6 收尾
当前模块：文档和架构图面试题验收
预计用时：15 分钟

### 1. 今日目标

- 补全第 1 周 Day 6 面试题的用户回答。
- 对用户回答做逐题评审，指出答对的点和面试表达可增强的点。
- 将第 6 天用户回答归档到 `docs/Compilation-of-Interview-Questions.md`。
- 明确下一次继续项目时的入口。

### 2. 今日输出物

- 已补全 `docs/Compilation-of-Interview-Questions.md` 中第 6 天 5 道面试题的用户回答。
- 已完成第 6 天面试题逐题评审。
- 已更新本文件、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 3. 完成情况

- 用户已能说明当前项目实现了最小 Coding Agent harness 的闭环。
- 用户已能区分 Agent 业务执行闭环和程序内部工具路由链路。
- 用户已能说明 README / 架构图必须和真实代码保持一致。
- 用户已能指出当前主要安全边界是 `workspace_root`，并能说出权限审批、危险命令分类等缺口。
- 用户已能说明当前先用 mock LLM 是为了稳定验证 Agent Loop 和工具路由控制流。
- 已运行 `python -m pytest -q`，结果为 `68 passed, 1 skipped`。

## 2026-06-08

日期：2026-06-08
当前阶段：第 1 周 Day 7
当前模块：周复盘和小重构
预计用时：45 分钟

### 1. 今日学习目标

- 复盘第 1 周从 Agent Loop 到 Tool Routing 的完整闭环。
- 能从源码角度讲清 `AgentLoop -> ToolRegistry -> Tool -> handler/runtime`。
- 学会在周复盘中区分“小而必要的重构”和“提前引入未来架构”。
- 用 TDD 补一个真实边界缺口：文件工具不能把非字符串 `path` 静默转成文件名。
- 更新第 1 周收口文档，为第 2 周 Tool System 深化做准备。

### 2. 所需前置知识

- Day 1：`Message`、`ToolCall`、`ScriptedLLM` 和最小 `AgentLoop`。
- Day 2：`Tool`、`ToolRegistry` 和工具路由。
- Day 3：文件工具、路径解析和 `workspace_root`。
- Day 4：`ShellRuntime`、`cwd`、timeout、输出结构和 runtime 分层。
- Day 5：默认 coding 工具注册表和多工具调用链路。
- Day 6：README、架构图和面试表达。

### 3. 今日必须理解的知识点

- 周复盘不是大重构；它的目标是确认当前闭环是否清楚、稳定、可测试、可解释。
- 工具参数来自 LLM 的结构化输出，不能把坏参数静默转成看似可执行的输入。
- `path=123` 这类坏参数如果被转成 `"123"`，`read_file` 会变成错误的文件读取，`write_file` 甚至会写出意外文件。
- TDD 的 RED 价值在于先证明测试真的能抓住缺口，再做最小修复。
- 第 1 周代码仍是 Agent harness 骨架，不应该在 Day 7 提前引入 planner、权限系统或真实 LLM。

### 4. 今日代码 / 文档任务

- 跑 Day 7 基线验证：`python -m pytest -q`、`python examples\01_minimal_agent.py`、`python -m compileall src examples -q`。
- 复盘 `src/pca/core/`、`src/pca/tools/`、`src/pca/runtime/` 和 `tests/`。
- 在 `tests/test_file_tools.py` 中补充非字符串 `path` 的 RED 测试。
- 在 `src/pca/tools/file_tools.py` 中让 `_resolve_workspace_path(...)` 明确拒绝非字符串路径。
- 更新 `README.md`、学习笔记、资料库、实现日志、下一步行动和每日面试题归档。

### 5. 今日资料推荐

- pytest assertion 官方文档：https://docs.pytest.org/en/stable/how-to/assert.html
- Python `pathlib` 官方文档：https://docs.python.org/3.11/library/pathlib.html
- Mermaid 语法官方参考：https://mermaid.js.org/intro/syntax-reference.html
- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling

### 6. 今日输出物

- `tests/test_file_tools.py` 新增非字符串路径边界测试。
- `src/pca/tools/file_tools.py` 新增路径参数类型校验。
- Day 7 周复盘学习笔记。
- Day 7 面试题归档。
- 更新后的 `README.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 7. 完成情况

- 已完成第 1 周代码复盘：当前主链路保持在 `AgentLoop -> ToolRegistry -> Tool -> handler/runtime`。
- 已确认不做大架构调整，不提前引入 planner、权限系统或真实 LLM。
- 已跑 Day 7 初始基线：`python -m pytest -q` 为 `66 passed, 1 skipped`；示例脚本和编译验证通过。
- 已按 TDD 新增 RED 测试，证明 `path=123` 会被错误地当作文件名处理。
- 已修复 `_resolve_workspace_path(...)`，让文件工具明确拒绝非字符串 `path`。
- 已验证 `python -m pytest tests\test_file_tools.py -q` 为 `25 passed, 1 skipped`。
- 已验证 `python -m pytest -q` 为 `68 passed, 1 skipped`。
- 已更新第 1 周收口文档。
- Day 6 和 Day 7 面试题用户回答均已补全并归档。

## 2026-06-08

日期：2026-06-08
当前阶段：第 1 周 Day 6
当前模块：文档和架构图
预计用时：45 分钟

### 1. 今日学习目标

- 复盘第 1 周 Day 1 到 Day 5 已经完成的最小 Coding Agent 闭环。
- 能用作品集和面试语言解释 `user -> LLM -> tool_call -> tool_result -> LLM -> final_answer`。
- 能区分 Agent 执行闭环和工具路由链路。
- 把 README、架构图、学习笔记和面试讲解稿整理成可继续维护的项目文档。

### 2. 所需前置知识

- Day 1：`Message`、`ToolCall`、`AgentLoop`、`ScriptedLLM`。
- Day 2：`Tool`、`ToolRegistry`、工具注册和执行。
- Day 3：文件工具和 `workspace_root` 边界。
- Day 4：shell runtime、`cwd`、timeout 和命令结果结构。
- Day 5：默认 coding 工具注册表和多工具路由集成。

### 3. 今日必须理解的知识点

- README 是项目入口，不只是运行说明；它要表达项目目标、当前能力、架构图、运行方式和安全边界。
- 架构图要画真实调用链，不画和代码不一致的未来设想。
- `ToolCall` 是 LLM 的调用意图，真正执行发生在程序侧的 `ToolRegistry -> Tool -> handler/runtime`。
- 工具结果必须写回 `message history`，否则 LLM 下一轮无法基于真实环境反馈继续决策。
- Day 6 是作品集表达和面试表达，不新增架构边界，因此不需要新增 ADR。

### 4. 今日代码 / 文档任务

- 更新 `README.md`，补齐当前能力、运行方式、核心架构图和面试讲解要点。
- 新增 `docs/10_WEEK1_INTERVIEW_SCRIPT.md`，沉淀第 1 周面试讲解稿初稿。
- 更新 `docs/05_LEARNING_NOTES.md`，新增 Day 6 文档和架构图学习笔记。
- 更新 `docs/04_RESOURCE_LIBRARY.md`，补充 Day 6 资料链接。
- 收尾时更新 `docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 5. 今日资料推荐

- ReAct 论文 arXiv 页面：https://arxiv.org/abs/2210.03629
- Google Research ReAct 介绍：https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/
- Mermaid 官方语法参考：https://mermaid.js.org/intro/syntax-reference.html
- GitHub Docs：README 和个人资料 README 说明：https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling

### 6. 今日输出物

- 更新后的 `README.md`。
- `docs/10_WEEK1_INTERVIEW_SCRIPT.md`。
- Day 6 文档和架构图学习笔记。
- Day 6 面试题归档。

### 7. 完成情况

- 已复盘第 1 周 Day 1 到 Day 5 的核心闭环。
- 已更新 README，使其反映 Day 6 当前能力、架构图、运行方式、测试方式和面试讲解要点。
- 已新增第 1 周面试讲解稿初稿：`docs/10_WEEK1_INTERVIEW_SCRIPT.md`。
- 已在学习笔记中新增 Day 6 文档和架构图记录。
- 已补充 Day 6 资料链接。
- 已运行 `python -m pytest -q`，结果为 `66 passed, 1 skipped`。
- 已运行 `python examples\01_minimal_agent.py`，示例输出完整 `user -> assistant -> tool:echo -> assistant` 链路。
- 已运行 `python -m compileall src examples -q`，源码和示例均可编译。
- Day 6 学习任务完成，下一步进入第 1 周 Day 7：周复盘和小重构。

## 2026-06-08

日期：2026-06-08
当前阶段：第 1 周 Day 5
当前模块：整合 Loop + Tools
预计用时：45 分钟

### 1. 今日学习目标

- 理解 Day 5 为什么不是继续新增单个工具，而是验证 `AgentLoop` 和多个工具的统一路由。
- 理解默认 coding 工具注册表的作用：把 `read_file`、`write_file`、`run_command` 组合成一个 `ToolRegistry`。
- 理解多工具调用结果如何按顺序写回 `message history`，让 LLM 可以继续基于工具结果回答。

### 2. 所需前置知识

- Day 1：`AgentLoop`、`Message`、`ToolCall` 和 `message history`。
- Day 2：`Tool` 和 `ToolRegistry` 的注册、查找和执行。
- Day 3：`read_file` / `write_file` 的 `workspace_root` 边界。
- Day 4：`run_command`、`ShellRuntime`、`cwd`、`timeout_seconds` 和结构化命令结果。

### 3. 今日必须理解的知识点

- `AgentLoop` 不应该直接依赖具体工具类，只应该依赖 `ToolRegistry.run(...)`。
- 多个工具统一注册后，路由链路仍然是 `ToolCall -> ToolRegistry -> Tool -> handler/runtime -> tool message`。
- `write_file` 的工具结果是 `"ok"`，`read_file` 的工具结果是文件文本，二者都必须进入 `message history`。
- 默认工具注册表只是组合入口，不替代权限系统、planner 或真实 LLM。

### 4. 今日代码任务

- 新增 `create_coding_tool_registry()`，统一注册内置 coding 工具。
- 新增 `tests/test_loop_tools_integration.py`，覆盖 `AgentLoop` 连续调用 `write_file` 和 `read_file` 的集成链路。
- 保持 `AgentLoop` 主循环不重构，先用集成测试证明现有路由能力成立。

### 5. 今日资料推荐

- OpenAI Function calling / tool calling guide：https://platform.openai.com/docs/guides/function-calling
- Claude tool use overview：https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- mini-SWE-agent GitHub：https://github.com/SWE-agent/mini-swe-agent
- mini-SWE-agent CLI docs：https://mini-swe-agent.com/latest/usage/mini/

### 6. 今日输出物

- `src/pca/tools/__init__.py` 中的 `create_coding_tool_registry()`。
- `tests/test_loop_tools_integration.py`。
- Day 5 Loop + Tools 学习笔记。

### 7. 完成情况

- 已按 TDD 写 RED 测试，失败原因是 `pca.tools` 尚无 `create_coding_tool_registry`。
- 已实现默认 coding 工具注册表，注册 `ReadFileTool`、`WriteFileTool` 和 `ShellCommandTool`。
- 已验证 `AgentLoop` 可以通过默认工具注册表完成 `write_file -> read_file -> final answer`。
- 已运行 `python -m pytest tests\test_loop_tools_integration.py -q`，结果为 `1 passed`。
- 已运行 `python -m pytest -q`，结果为 `66 passed, 1 skipped`。
- 已运行 `python examples\01_minimal_agent.py`，示例输出完整 `user -> assistant -> tool:echo -> assistant` 链路。
- 已运行 `python -m compileall src examples -q`，源码和示例均可编译。
- 已完成 Day 5 面试题回答评审。
- 已将第 5 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- Day 5 学习验收通过，下一步进入第 1 周 Day 6：文档和架构图。

## 2026-06-07

日期：2026-06-07
当前阶段：项目公开发布准备
当前模块：README / .gitignore / GitHub remote
预计用时：20 分钟

### 1. 今日目标

- 让 GitHub 首页能清晰说明项目目标、当前进度、运行方式和学习路线。
- 补强 Git 忽略规则，避免缓存、虚拟环境、环境变量、IDE 状态和本地临时文件被发布。
- 配置远程仓库并发布到 `https://github.com/nanhanq1/personal-coding-assistant.git`。

### 2. 今日输出物

- 更新 `README.md`。
- 更新 `.gitignore`。
- 更新 `docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 3. 完成情况

- 已完成 README 和 `.gitignore` 的发布前补充。
- 发布前继续执行测试、Git 索引清理、提交和 push。
- 本次不改变学习主线；下一次继续项目仍进入第 1 周 Day 5：整合 Loop + Tools。

## 2026-06-07

日期：2026-06-07
当前阶段：第 1 周 Day 4 收尾
当前模块：shell runtime 复盘与面试题归档
预计用时：15 分钟

### 1. 今日学习目标

- 检查用户是否理解 shell runtime 的风险、工作区边界、输出字段和 tool/runtime 分层。
- 将 Day 4 面试题、用户回答和标准回答沉淀到每日面试题归档。
- 明确下一步进入 Day 5：整合 Loop + Tools。

### 2. 今日输出物

- 已评审 Day 4 五个面试题回答。
- 已更新 `docs/Compilation-of-Interview-Questions.md`，追加第 4 天记录。
- 已更新 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 3. 完成情况

- 已增强 shell runtime 的 `command` 参数，支持 `list[str]` 命令。
- 已保留字符串命令兼容路径：字符串使用 `shell=True`，列表使用 `shell=False`。
- 已补充测试：列表命令执行、带空格参数保留、非法列表拒绝。
- 用户已能说明 shell runtime 比文件工具危险，因为它可以影响本机程序和文件。
- 用户已能说明 `workspace_root` 是命令运行边界。
- 用户已能区分 `stdout`、`stderr`、`returncode`、`timed_out` 和 `duration_ms`。
- 用户已能说明 `ShellCommandTool` 负责工具包装，`ShellRuntime` 负责真实执行。
- 已补充说明：越界 `cwd` 不能直接放行，应进入权限审批或扩大授权工作区；`command` 列表形式和 `shell=False` 是后续安全增强方向。
- 下一步进入第 1 周 Day 5：整合 Loop + Tools。

## 2026-06-06

日期：2026-06-06
当前阶段：第 1 周 Day 4 shell runtime 工程化拆分与工业级代码审查
当前模块：`AgentLoop` / `ToolRegistry` / `FileTool` / `ShellRuntime` / Responses API 实验脚本
预计用时：1 小时

### 1. 今日学习目标

- 理解 shell runtime 为什么比文件工具更危险。
- 理解命令执行必须记录 `stdout`、`stderr`、`returncode` 和超时状态。
- 理解工作目录必须限制在 `workspace_root` 内。
- 理解 Windows 输出编码和符号链接权限会影响测试设计。
- 理解工业级代码审查不只看 happy path，还必须看坏输入、工具失败、密钥、目录和超时边界。

### 2. 所需前置知识

- Python `subprocess.run(...)`。
- `cwd`、`timeout`、`env`、`stdout`、`stderr`、`returncode`。
- Day 2 的 `Tool` / `ToolRegistry` 调用链。
- Day 3 的 `workspace_root` 边界思想。

### 3. 今日必须理解的知识点

- `Tool` 是包装器，工具类如果继承它，必须在初始化时传入 `handler`。
- shell 命令会对真实运行环境产生影响，因此必须先限制 `cwd`。
- 相对 `cwd` 应以 `workspace_root` 为基准解析，而不是以当前进程目录为基准。
- Windows 下子进程输出路径可能包含中文字符，解码应使用本机 locale。
- API key 不能硬编码在源码中，实验脚本也不能导入时就创建真实 client。
- 工具失败要进入 `message history`，让 LLM 有机会恢复，而不是直接丢失轨迹。

### 4. 今日代码任务

- 评审并修复 `src/pca/tools/file_tools.py` 中工具类继承 `Tool` 的初始化问题。
- 实现并修复 `src/pca/tools/shell_tools.py` 的 `ShellCommandTool`。
- 新增 `tests/test_shell_runtime.py`，覆盖成功命令、失败命令、工作目录、超时、环境变量、stdout/stderr 和 `ToolRegistry` 集成。
- 调整 `tests/test_file_tools.py` 中与平台权限和路径语义不一致的测试。
- 对当前已实现代码做工业级审查，并保留修改前快照用于对比。
- 补充工具元数据、消息结构、AgentLoop、文件工具、shell runtime 和 API 实验脚本的安全边界测试。

### 5. 今日资料推荐

- Python `subprocess` 官方文档：https://docs.python.org/3/library/subprocess.html
- pytest monkeypatch 官方文档：https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- PowerShell `pwsh` 命令行说明：https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pwsh
- Python `locale` 官方文档：https://docs.python.org/3/library/locale.html

### 6. 今日输出物

- `ShellCommandTool`
- `ShellRuntime.run(arguments: dict[str, Any]) -> dict[str, Any]`
- `run_command(arguments: dict[str, Any]) -> dict[str, Any]`
- `tests/test_shell_runtime.py`
- ADR-0004：shell runtime 先实现受工作区限制的同步命令执行

### 7. 完成情况

- 已修复工具类继承 `Tool` 时缺少 `handler` 的问题。
- 已实现 `ShellCommandTool` 和函数形式 `run_command(...)`。
- 已补充 shell runtime 测试。
- 已修正文件工具测试中的平台假设。
- 已将 subprocess 执行逻辑从 `ShellCommandTool` 拆到 `ShellRuntime`，让 tool 层只负责工具包装和注册。
- 已修复 `timeout_seconds` 字符串数字会传入 `subprocess.run(...)` 导致 TypeError 的问题。
- 已让非法 `timeout_seconds` 在参数边界抛 `ValueError`，不再被伪装成命令执行失败。
- 已将测试中的子进程 Python 命令改为使用 `sys.executable`，降低 PATH 依赖。
- 已更新教学要求：从“不能直接给代码”调整为“先让被教学者真正理解代码逻辑，再给出完整、安全、全面、工程级代码”。
- 已创建修改前代码快照：`docs/code_reviews/2026-06-06-before-industrial-refactor/`，其中旧版 API key 已脱敏。
- 已移除正式源码中的硬编码 API key，Responses API 实验脚本改为从环境变量惰性创建 client。
- 已补充 `tests/test_api_experiments.py`，防止 `src/` 再出现硬编码 key，并验证实验模块导入时不创建真实 client。
- 已为 `Tool`、`ToolRegistry`、`Message`、`ToolCall`、`ScriptedLLM`、`AgentLoop`、文件工具和 shell runtime 增加更严格边界校验。
- 已将占位源码和示例的说明文字改为中文。
- 已按用户要求，在核心修改后的新源码中加入“修改前旧代码”注释片段，方便直接对比；涉及 API key 的旧代码片段已脱敏。
- 已运行 `python -m pytest tests\test_file_tools.py tests\test_shell_runtime.py -q`，结果为 `37 passed, 1 skipped`。
- 已运行 `python -m pytest -q`，结果为 `45 passed, 1 skipped`。
- 已运行工业级加固目标测试：`python -m pytest tests\test_tools.py tests\test_agent_loop.py tests\test_file_tools.py tests\test_shell_runtime.py tests\test_api_experiments.py -q`，结果为 `61 passed, 1 skipped`。
- 已运行最新全量测试：`python -m pytest -q`，结果为 `62 passed, 1 skipped`。
- 已运行 `python examples\01_minimal_agent.py`，示例输出完整 `user -> assistant -> tool -> assistant` 链路。
- 已运行 `python -m compileall src examples -q`，源码和示例均可编译。
- 已扫描 `src/` 和修改前快照，未再发现 `sk-` 字面量。
- 已完成 Day 4 shell runtime 复盘与面试题回答评审。
- 已将第 4 天面试题、用户回答和标准回答追加到 `docs/Compilation-of-Interview-Questions.md`。
- 下一步进入第 1 周 Day 5：整合 Loop + Tools，重点是多工具调用和工具路由链路。

## 2026-06-05

日期：2026-06-05
当前阶段：第 1 周 Day 3 收尾
当前模块：文件工具面试题评审与归档
预计用时：20 分钟

### 1. 今日学习目标

- 检查用户对文件工具四个核心问题的理解是否到位。
- 将 Day 3 面试题、用户回答和标准回答沉淀到每日面试题归档。
- 明确 Day 3 文件工具在整体架构中的位置，并准备进入 Day 4 shell runtime。

### 2. 今日输出物

- 已评审 Day 3 四个面试题回答。
- 已更新 `docs/Compilation-of-Interview-Questions.md`，追加第 3 天记录。
- 已更新 `docs/05_LEARNING_NOTES.md`，补充 Day 3 文件工具学习笔记和流程图。
- 已更新 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 3. 完成情况

- 用户已能说明 LLM 只能生成文本，真实写入需要文件工具。
- 用户已能说明 `read_file` 返回值进入上下文后帮助 LLM 决策。
- 用户已能指出 workspace 边界的安全意义。
- 用户已能区分 `ToolCall` 的调用意图和 `read_file()` 的真实执行。
- 已补齐 Day 3 学习笔记、调用链、流程图、检查问题和工业级增强方向。
- 已使用项目内临时目录运行 `python -m pytest -q`，结果为 `16 passed`。

## 2026-06-04

日期：2026-06-04
当前阶段：第 1 周 Day 3 文件工具
当前模块：`read_file` / `write_file` 代码评审、补充实现与测试
预计用时：1 小时

### 1. 今日学习目标

- 理解文件工具为什么是 Coding Agent 从“会调用函数”走向“能操作代码库”的第一步。
- 理解路径解析、工作区边界和文件读写错误的职责划分。
- 学会用测试验证安全边界，而不是依赖某个系统路径不存在来碰巧通过。
- 理解文件工具如何继续复用 Day 2 的 `Tool` / `ToolRegistry` 抽象。

### 2. 所需前置知识

- Python `pathlib.Path` 的路径拼接、`resolve()`、`read_text()` 和 `write_text()`。
- pytest `tmp_path` fixture。
- `ValueError`、`KeyError`、`FileNotFoundError` 的区别。
- Day 2 调用链：`AgentLoop -> ToolRegistry.run(...) -> Tool.run(...) -> handler(arguments)`。

### 3. 今日必须理解的知识点

- `read_file` / `write_file` 的参数来自 LLM 生成的 `ToolCall.arguments`，因此必须做输入校验。
- 文件工具不能只关心“能读写”，还必须限制在 `workspace_root` 内。
- 空字符串是合法文件内容，不能把空内容和缺少内容混为一谈。
- `tmp_path` 让文件读写测试不污染真实项目文件。

### 4. 今日代码任务

- 评审用户实现的 `src/pca/tools/file_tools.py` 和 `tests/test_file_tools.py`。
- 修复类型标注、路径校验、编码、异常语义和 workspace 边界问题。
- 补充 `workspace_root` 路径解析逻辑。
- 补充文件读写、空内容、缺少内容、路径越界和 `ToolRegistry` 集成测试。

### 5. 今日资料推荐

- Python `pathlib` 官方文档：https://docs.python.org/3/library/pathlib.html
- pytest `tmp_path` 官方文档：https://docs.pytest.org/en/stable/how-to/tmp_path.html
- OpenAI Agents SDK Tools 文档：https://openai.github.io/openai-agents-python/tools/
- Microsoft Learn Python on Windows 路径说明：https://learn.microsoft.com/en-us/windows/python/
- 视频 / 课程页面：Real Python `pathlib` 视频课程：https://realpython.com/videos/pathlib-python-overview/

### 6. 今日输出物

- `read_file(arguments: dict[str, Any]) -> str`
- `write_file(arguments: dict[str, Any]) -> str`
- `_resolve_workspace_path(...)`
- `tests/test_file_tools.py`
- ADR-0003：文件工具必须限制在 `workspace_root` 内

### 7. 完成情况

- 已完成第一轮代码评审和补充实现。
- 已将文件工具限制在 `workspace_root` 内。
- 已补充测试：读取、写入、空内容、缺少内容、空路径、路径越界和 `ToolRegistry` 集成。
- 已运行 `python -m pytest tests\test_file_tools.py -q`，结果为 `8 passed`。
- 已使用项目内临时目录运行 `python -m pytest -q`，结果为 `16 passed`。
- 已完成 Day 3 面试题回答评审，并归档到 `docs/Compilation-of-Interview-Questions.md`。
- 已补齐 Day 3 学习笔记和流程图。
- 下一步进入第 1 周 Day 4：shell runtime 雏形。

## 2026-06-03

日期：2026-06-03  
当前阶段：第 1 周 Day 3 前规则补充  
当前模块：每日面试题归档规则  
预计用时：10 分钟

### 1. 今日学习目标

- 明确后续完成一天任务后，面试题不只在对话里出现，还要沉淀到项目文件中。
- 固定每日面试题归档格式，方便后续复盘、面试训练和作品集整理。

### 2. 今日输出物

- 已新增 `docs/Compilation-of-Interview-Questions.md`。
- 已补充每日面试题归档规则：标题为“第几天 + 年月日”，内容包含面试题、用户回答和标准回答。
- 已把该规则同步到 `AGENTS.md`、`docs/CODEX_PROJECT_BRIEF.md` 和 `docs/09_NEXT_ACTIONS.md`。
- 已补全第 1 天和第 2 天的面试题归档内容。
- 已同步更新 `docs/08_INTERVIEW_BANK.md` 的 Tool System 面试题。

### 3. 完成情况

- 已确认仓库中原有 `docs/08_INTERVIEW_BANK.md` 是模块级题库。
- 已新增 `docs/Compilation-of-Interview-Questions.md` 作为每日面试题汇总文件。
- 下一次完成每日学习任务后，必须把当天面试题、用户回答和标准回答追加到该文件。
- 已将第 1 天 Agent Loop 面试题写入汇总文件；用户回答根据 2026-05-31 学习验收记录整理。
- 已将第 2 天 Tool System 面试题写入汇总文件；当前没有找到用户原回答记录，用户回答字段先标记为“待补充”。

## 2026-06-02

日期：2026-06-02  
当前阶段：第 1 周 Day 2 收尾复核  
当前模块：Tool System 文档收尾与测试确认  
预计用时：15 分钟

### 1. 今日学习目标

- 确认 Day 2 Tool System 的代码和文档处于可继续状态。
- 复核当前测试结果，保证下一次可以直接进入 Day 3 文件工具。
- 明确本次没有新增架构决策，后续仍沿用 `ToolRegistry` 作为工具路由入口。

### 2. 所需前置知识

- 能读懂 `Tool`、`ToolRegistry` 和 `AgentLoop` 的职责边界。
- 能理解 `python -m pytest -q` 的通过结果与 warning 的区别。
- 能根据 `docs/09_NEXT_ACTIONS.md` 判断下一次继续项目的入口。

### 3. 今日必须理解的知识点

- 收尾复核不是新增功能开发，而是确认当前状态、测试结果和下一步入口。
- 当前 `.pytest_cache` warning 是本地缓存目录写入权限问题，不代表业务测试失败。
- Day 3 文件工具会建立在 Day 2 的 `ToolRegistry` 之上。

### 4. 今日代码任务

- 本次没有新增或修改业务代码。
- 运行项目测试，确认 Day 2 代码仍然通过。
- 更新 `docs/02_DAILY_TASKS.md`、`docs/07_IMPLEMENTATION_LOG.md` 和 `docs/09_NEXT_ACTIONS.md`。

### 5. 今日资料推荐

- pytest 官方文档：重点看 test discovery、warning summary 和 cache provider。
- Python pathlib 官方文档：为 Day 3 文件工具提前理解路径对象。
- 视频搜索关键词：`pytest warning cacheprovider WinError 5`、`Python pathlib file read write tutorial`。
- 预习资料：OpenAI Agents SDK Tools 文档中关于工具输入输出的描述方式。

### 6. 今日输出物

- Day 2 收尾复核记录。
- 最新测试结果记录。
- Day 3 继续指令确认。

### 7. 完成情况

- 已运行 `python -m pytest -q`，结果为 `8 passed, 1 warning in 0.16s`。
- 当前 warning 仍是 `.pytest_cache` 写入权限问题，不影响功能验收。
- 已确认本次没有新增架构决策，`docs/06_ARCHITECTURE_DECISIONS.md` 无需更新。
- 下一次继续项目时进入第 1 周 Day 3：文件工具 `read_file` / `write_file` 入门。

## 2026-06-01

日期：2026-06-01  
当前阶段：第 1 周 Tool System  
当前模块：Day 2 Tool 抽象与 ToolRegistry  
预计用时：1-1.5 小时

### 1. 今日学习目标

- 理解为什么 Agent 不能长期依赖 `dict[str, callable]` 管理工具。
- 理解 `ToolCall`、`Tool`、`ToolRegistry` 和 `AgentLoop` 的职责边界。
- 实现工具注册、查找、执行和错误处理的最小闭环。
- 把 `AgentLoop` 从直接调用函数升级为通过 `ToolRegistry.run(...)` 执行工具。

### 2. 所需前置知识

- Python `dataclass` 的基本用法。
- `Callable[[dict[str, Any]], Any]` 这种函数类型标注的含义。
- 字典查找、重复 key、`KeyError` 的语义。
- Day 1 的 `ToolCall -> tool_result -> assistant final answer` 调用链。

### 3. 今日必须理解的知识点

- `ToolCall` 是 LLM 发出的结构化调用意图，不是真正执行工具。
- `Tool` 是程序侧对真实工具函数的包装，包含名称、描述和执行入口。
- `ToolRegistry` 是工具系统的路由表，负责注册、查找和执行工具。
- `AgentLoop` 不应该关心具体工具函数，只需要把 `tool_call.name` 和 `tool_call.arguments` 交给 registry。

### 4. 今日代码任务

- 实现 `src/pca/tools/base.py` 的 `Tool` 数据结构。
- 实现 `src/pca/tools/registry.py` 的 `ToolRegistry`。
- 新增 `tests/test_tools.py`，覆盖注册、获取、执行、重复注册和未知工具。
- 更新 `src/pca/core/agent_loop.py`，让 Agent Loop 通过 `ToolRegistry` 执行工具。
- 更新 `examples/01_minimal_agent.py`，保持示例脚本可从仓库根目录直接运行。

### 5. 今日资料推荐

- OpenAI Agents SDK：重点看 Tools 概念，理解工具为什么需要描述和统一执行接口。
- mini-SWE-agent：继续观察它如何把工具执行结果写回 trajectory。
- 视频搜索关键词：`AI agent tool registry Python`、`tool calling agent from scratch`。
- 复习资料：ReAct 论文中 action / observation 的交替结构。

### 6. 今日输出物

- `Tool` 抽象。
- `ToolRegistry`。
- 工具系统单元测试。
- Agent Loop 与 ToolRegistry 的集成测试。
- 可运行示例脚本。
- Day 2 架构决策记录。

### 7. 完成情况

- 已完成 `Tool` 和 `ToolRegistry` 的最小实现。
- 已完成工具注册、查找、执行、重复注册和未知工具的测试。
- 已将 `AgentLoop` 从裸 `dict[str, callable]` 升级为使用 `ToolRegistry`。
- 已修复示例脚本导入顺序，保证 `python examples/01_minimal_agent.py` 可从仓库根目录运行。
- 已运行 `python -m pytest -q`，结果为 `8 passed, 1 warning`。
- 当前 warning 是 `.pytest_cache` 写入权限问题，不影响功能验收。
- 下一次继续项目时进入第 1 周 Day 3：文件工具 `read_file` / `write_file` 入门。

## 2026-05-31

日期：2026-05-31  
当前阶段：第 1 周 Agent Loop -> Tool System 准备  
当前模块：Day 1 学习验收与 Day 2 准备  
预计用时：15 分钟

### 1. 今日学习目标

- 确认用户已经读懂 Day 1 最小 Agent Loop 代码。
- 检查用户是否能用自己的话解释 Agent Loop、Message history、ToolCall、mock LLM 和 max_turns。
- 判断是否可以进入第 1 周 Day 2：Tool System 入门。

### 2. 今日检查结果

- 用户已完成 5 个检查问题。
- Agent Loop 的解释已经抓住核心：`user input -> LLM -> tool_call -> tool_result 写回 message history -> LLM -> final answer`。
- Message history 的理解已经到位：它是 Agent 的短期工作记忆和可回放轨迹。
- ToolCall 与普通函数调用的区别已基本掌握：ToolCall 是 LLM 发出的结构化调用意图，普通函数调用是程序逻辑直接执行。
- mock LLM 的意义已掌握：排除真实 LLM 的随机性、网络和 API 干扰，专注验证 Agent Loop 控制流。
- max_turns 的风险意识已建立：避免幻觉、工具错误或停止条件失败导致无限循环、成本失控和内存增长。

### 3. 完成情况

- Day 1 学习验收通过。
- 已修复核心模块和测试中不规范的 `src.pca...` 导入，统一为标准 `pca...` 导入。
- 已运行 `python -m pytest -q`，结果为 `2 passed, 1 warning`。
- 当前无阻塞。
- 下一次继续项目时进入第 1 周 Day 2：Tool System 入门。

## 2026-05-27

日期：2026-05-27  
当前阶段：第 1 周 Agent Loop  
当前模块：项目长期教学规则更新  
预计用时：10 分钟

### 1. 今日学习目标

- 明确后续教学采用“先用户实现，再评审，再注释，再参考实现对比”的训练方式。

### 2. 今日输出物

- 已更新项目教学规则。
- 已写入 Codex 长期记忆更新说明。
- 已补充代码注释默认使用中文的长期要求。
- 已补充每日任务必须包含资料推荐、所需知识和网页版视频 / 课程页面的长期要求。
- 已补充每日任务必须包含面试题的长期要求。
- 已补充代码评审后的阶段定位与架构、完整性、安全、容错问题分析要求。
- 已补充资料推荐和视频推荐必须提供有效、正确、可访问链接的长期要求。

### 3. 完成情况

- 已把“不先给出现成完整代码”的教学方式写入 `AGENTS.md`。
- 已把同样规则写入 `docs/CODEX_PROJECT_BRIEF.md`。
- 已把“新增或修改代码注释默认使用中文”的要求写入项目规则和长期提示词。
- 已把“每日任务增加资料推荐、所需知识、网页版视频 / 课程页面”的要求写入项目规则和长期提示词。
- 已把“每日任务增加面试题”的要求写入项目规则和长期提示词。
- 已把“用户写完代码并完成评审、注释、参考实现对比后，必须指出当前代码阶段位置及其在整体架构、完整代码、安全、容错中的问题”的要求写入项目规则和长期提示词。
- 已把“资料推荐和视频推荐必须提供有效、正确、可访问链接，链接不确定时先验证”的要求写入项目规则和长期提示词。
- 下一次继续项目时，仍从 Tool System 入门开始，但教学方式按新规则执行。

## 2026-05-26

日期：2026-05-26  
当前阶段：第 1 周 Agent Loop  
当前模块：最小 Agent Loop  
预计用时：1.5-2 小时

### 1. 今日学习目标

- 理解 Agent Loop 为什么是 Coding Agent 的最小骨架。
- 理解 message history 如何把用户、助手和工具结果串起来。
- 理解 mock LLM 如何帮助我们先验证架构，而不是过早接入真实 API。
- 理解 tool_call -> tool_result -> continue 的最小闭环。

### 2. 今日核心概念

| 概念 | 一句话解释 | 类比 | 代码位置 |
| --- | --- | --- | --- |
| Message | Agent 和 LLM 之间传递上下文的标准记录 | 聊天记录本 | `src/pca/core/messages.py` |
| ToolCall | LLM 请求程序执行外部能力的结构化指令 | 让助教帮忙查资料的便条 | `src/pca/core/messages.py` |
| Agent Loop | 不断让 LLM 思考、调用工具、读取结果并继续回答的循环 | 学生做题时查资料、修正答案、再提交 | `src/pca/core/agent_loop.py` |

### 3. 今日代码任务

实现：

- `src/pca/core/messages.py`
- `src/pca/core/mock_llm.py`
- `src/pca/core/agent_loop.py`
- `tests/test_agent_loop.py`
- `examples/01_minimal_agent.py`

### 4. 今日最小验收标准

- `python -m pytest -q` 通过。
- 能手动运行 `python examples/01_minimal_agent.py`。
- 能看到 `tool_call -> tool_result -> final_answer` 的完整流程。

### 5. 今日资料推荐

- 官方文档：OpenAI Agents SDK 的 Tools 和 Runner 概念。
- GitHub 源码：mini-SWE-agent 的 agent loop 和 trajectory。
- 视频搜索关键词：`AI Agents from scratch tool calling tutorial`。
- 论文：ReAct，重点读它如何把 Reasoning 和 Acting 交替组织起来。

### 6. 今日输出物

- 最小 Agent Loop 代码。
- 单元测试。
- 学习笔记。
- Agent Loop 流程图。
- 3 个面试题。

### 7. 完成情况

- 已初始化项目文档和 Python 包结构。
- 已用 TDD 写出 `tests/test_agent_loop.py` 并观察到 RED。
- 已实现最小 Agent Loop、message schema、mock LLM。
- 已补充 `tests/test_examples.py`，保证示例脚本能从仓库根目录直接运行。
- 已运行 `python -m pytest -q`，结果为 `2 passed`。
- 已运行 `python examples/01_minimal_agent.py`，看到 `user -> assistant -> tool -> assistant` 完整链路。
