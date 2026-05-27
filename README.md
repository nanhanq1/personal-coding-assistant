# Personal Coding Assistant Agent

这是一个学习优先的 Personal Coding Assistant Agent 项目。目标不是快速堆功能，而是从零实现 Coding Agent 的核心机制，并逐步升级到工业级雏形。

## 当前阶段

- 第 1 周：Agent Loop
- 当前能力：最小 `LLM -> tool_call -> tool_result -> final_answer` 闭环

## 运行测试

```powershell
python -m pytest -q
```

## 运行示例

```powershell
python examples/01_minimal_agent.py
```

