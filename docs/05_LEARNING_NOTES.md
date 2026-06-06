# Learning Notes

## 工业级代码审查：2026-06-06

### 1. 直觉

“代码能跑”只说明 happy path 成立；“工业级代码”还要回答坏输入、工具失败、目录错误、超时、密钥泄露和后续恢复怎么办。

### 2. 本次审查出的关键问题

- 早期实验脚本在源码中硬编码 API key，这是高风险凭据泄露问题。
- 实验脚本导入时就创建真实 OpenAI client，会让包导入依赖网络配置和第三方 SDK。
- `Tool`、`ToolRegistry`、`Message` 和 `ToolCall` 没有在边界处拒绝坏数据。
- `AgentLoop` 直接抛出工具异常，导致 LLM 看不到失败原因，也无法恢复。
- 文件工具读目录时依赖 Windows 的 `PermissionError`，错误语义不稳定。
- shell runtime 对不存在的工作区、无效 `cwd`、超大超时值和空环境变量名缺少前置校验。

### 3. 加固后的调用链

```text
user_input
  -> AgentLoop 校验输入和 max_turns
  -> LLM.complete(messages) 必须返回 Message
  -> Message / ToolCall 校验消息结构
  -> ToolRegistry 校验工具名和 arguments
  -> Tool.run 校验 arguments 是 dict
  -> FileTool / ShellRuntime 做工作区、目录、超时、环境变量边界校验
  -> 成功结果或工具错误写回 message history
  -> LLM 可以继续恢复或给出最终回答
```

### 4. 本次保留的对比材料

- 修改前代码快照：`docs/code_reviews/2026-06-06-before-industrial-refactor/`
- 安全说明：快照中的旧版 API key 已替换为 `<REDACTED_API_KEY>`。
- 当前正式源码已新增测试，防止 `src/` 再出现硬编码 key。

### 5. 当前仍不是完整工业级的地方

- shell runtime 仍使用本机 shell，同步执行，还没有权限审批、命令风险分类、sandbox 和进程树清理。
- 文件工具还没有 diff 编辑、文件大小上限、二进制检测和写入前审批。
- Responses API 实验脚本仍只是学习材料，不是正式 LLM adapter。
- 错误回写目前是字符串形式，后续应升级为结构化 tool result 和可观测日志。

## Shell Runtime：第 4 天

### 1. 直觉

shell runtime 是 Coding Agent 真正“动手执行命令”的地方。文件工具只影响文件内容，shell 命令可以运行测试、启动进程、读取环境变量、卡住进程，甚至执行破坏性操作，所以必须先有清晰边界。

### 2. 一句话解释

`ShellRuntime` 负责受控执行命令，`ShellCommandTool` 负责把 Agent 的工具调用转发给 runtime。

### 3. 核心调用链

```text
LLM 生成 ToolCall
  -> AgentLoop 读取 tool_call.name 和 tool_call.arguments
  -> ToolRegistry.run(name, arguments)
  -> ShellCommandTool.run(arguments)
  -> ShellRuntime.run(arguments)
  -> subprocess.run(...)
  -> 返回 stdout / stderr / returncode / timed_out
  -> AgentLoop 把结果写回 message history
```

### 4. 流程图

```mermaid
flowchart TD
    A["LLM outputs run_command ToolCall"] --> B["AgentLoop"]
    B --> C["ToolRegistry.run"]
    C --> D["ShellCommandTool"]
    D --> E["ShellRuntime"]
    E --> F["Validate command, cwd, timeout"]
    F --> G{"cwd inside workspace_root?"}
    G -- "No" --> H["Raise ValueError"]
    G -- "Yes" --> I["subprocess.run"]
    I --> J["stdout / stderr / returncode / timed_out"]
    J --> K["Append tool result to message history"]
```

### 5. 技术原理

- `command` 必须是非空字符串。
- 相对 `cwd` 必须以 `workspace_root` 为基准解析。
- 解析后的 `cwd` 必须位于 `workspace_root` 内。
- `timeout_seconds` 要先规范化成正浮点数，再传给 `subprocess.run(...)`。
- 命令自身失败要保留 `returncode`，参数错误要直接抛 `ValueError`。
- `stdout` 给 Agent 看正常输出，`stderr` 给 Agent 判断错误原因，`returncode` 判断命令是否成功，`timed_out` 判断是否需要停止或重试。

### 6. 当前代码位置

- runtime：`src/pca/runtime/shell_runtime.py`
- tool：`src/pca/tools/shell_tools.py`
- 测试：`tests/test_shell_runtime.py`
- 架构决策：`docs/06_ARCHITECTURE_DECISIONS.md` 中的 ADR-0004

### 7. 工业级增强方向

- 接入权限系统，执行危险命令前请求用户确认。
- 增加命令 allowlist / denylist 和风险分类。
- 增加审计日志，记录命令、工作目录、退出码、耗时和 trace id。
- 增加进程树清理，避免超时后留下子进程。
- 增加 sandbox / docker runtime，减少宿主机风险。

## Agent Loop：第 1 天

### 1. 直觉

Agent Loop 就是让模型不只“一次性回答”，而是能在回答过程中请求工具、读取工具结果，然后继续思考。

### 2. 一句话解释

Agent Loop 是 `LLM -> tool_call -> tool_result -> LLM` 的循环控制器。

### 3. 流程图

```mermaid
flowchart TD
    A["User message"] --> B["LLM complete"]
    B --> C{"Has tool call?"}
    C -- "Yes" --> D["Run tool"]
    D --> E["Append tool result"]
    E --> B
    C -- "No" --> F["Final answer"]
```

### 4. 技术原理

- 所有输入、助手输出、工具结果都进入同一个 message history。
- LLM 根据 history 决定下一步：直接回答或发起工具调用。
- Agent Loop 负责执行工具，并把结果作为 `role=tool` 的消息写回 history。
- 当 LLM 返回没有 tool call 的 assistant message 时，循环结束。

### 5. 核心调用链

```text
AgentLoop.run(user_input)
  -> append user Message
  -> llm.complete(messages)
  -> append assistant Message
  -> execute assistant.tool_calls
  -> append tool Message
  -> llm.complete(messages)
  -> final assistant Message
```

### 6. 工业级增强方向

- 工具 schema 和参数校验。
- 多工具调用并发和顺序控制。
- 最大轮数、超时、重试和错误恢复。
- tool call trace、日志、成本统计。
- 权限系统和危险命令审批。

## 文件工具：第 3 天

### 1. 直觉

LLM 本身只能生成文本，不能直接改变磁盘上的代码文件。Coding Agent 要真正修改代码库，必须把 LLM 的文本决策交给文件工具执行。

文件工具是 Agent 从“会调用函数”走向“能操作代码库”的第一步：

- `read_file` 让 Agent 读取真实文件内容，而不是凭记忆或猜测回答。
- `write_file` 让 Agent 把生成的内容写回文件系统。
- `workspace_root` 限制工具只能在授权工作区内读写，避免影响其他目录。

### 2. 一句话解释

文件工具把 `ToolCall.arguments` 中的路径和内容转换成受控的文件系统读写操作。

### 3. 核心调用链

```text
LLM 生成 ToolCall
  -> AgentLoop 读取 tool_call.name 和 tool_call.arguments
  -> ToolRegistry.run(name, arguments)
  -> Tool.run(arguments)
  -> read_file(arguments) / write_file(arguments)
  -> 文件系统读写
  -> 返回工具结果
  -> AgentLoop 把结果写回 message history
```

### 4. 流程图

```mermaid
flowchart TD
    A["LLM outputs ToolCall"] --> B["AgentLoop receives tool call"]
    B --> C["ToolRegistry.run(name, arguments)"]
    C --> D["Tool.run(arguments)"]
    D --> E{"Tool name"}
    E -->|read_file| F["Resolve path inside workspace_root"]
    E -->|write_file| G["Resolve path inside workspace_root"]
    F --> H{"Path inside workspace?"}
    G --> H
    H -->|No| I["Raise ValueError"]
    H -->|Yes| J["Read or write file"]
    J --> K["Return tool result"]
    K --> L["Append result to message history"]
```

### 5. 技术原理

- `path` 来自工具参数，不能默认可信。
- `workspace_root` 是当前允许读写的工作区边界。
- 相对路径要拼到 `workspace_root` 后再解析。
- 绝对路径也必须位于 `workspace_root` 内。
- 路径越界属于非法请求，应该抛 `ValueError`。
- 文件不存在是环境事实，应该保留 `FileNotFoundError`。
- 空字符串是合法文件内容，不应该被当成缺少内容。
- 文件读写显式使用 `encoding="utf-8"`，减少跨平台编码差异。

### 6. 当前代码位置

- 实现：`src/pca/tools/file_tools.py`
- 测试：`tests/test_file_tools.py`
- 架构决策：`docs/06_ARCHITECTURE_DECISIONS.md` 中的 ADR-0003

### 7. 当前测试覆盖

- 读取文件内容。
- 读取不存在文件时抛 `FileNotFoundError`。
- 写入文件内容。
- 允许写入空字符串。
- 拒绝空路径。
- 拒绝工作区外路径。
- 缺少 `content` 时暴露工具调用错误。
- 文件工具可以注册进 `ToolRegistry` 并通过 `registry.run(...)` 执行。

### 8. 检查问题

1. 为什么 LLM 不能直接修改文件，而需要 `write_file`？
2. `read_file` 的返回值为什么要写回 message history？
3. `workspace_root` 防止了哪些风险？
4. 路径越界为什么应该抛 `ValueError`，而不是 `FileNotFoundError`？
5. 空字符串为什么是合法文件内容？
6. `ToolCall` 和真正执行 `read_file(arguments)` 有什么区别？

### 9. 工业级增强方向

- 增加 JSON Schema 或 Pydantic 参数校验。
- 增加文件大小限制，避免一次读入过大文件。
- 增加二进制文件检测。
- 增加 `edit_file`，用补丁或 diff 修改局部内容，而不是整文件覆盖。
- 增加权限审批，写文件前让用户确认高风险操作。
- 增加 audit log，记录工具名、参数、结果、错误、耗时和 trace id。
- 增加 checkpoint 或 git diff，用于真正回滚文件状态。
