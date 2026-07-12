# Implementation Log

本文件只保留当前活跃实现记录。历史记录归档在 `docs/archive/implementation_log/`。

## 历史归档路由

- Week 6 Day 1-Day 7 的代码、文档、验证、能力边界与交接证据：`docs/archive/implementation_log/2026-07-10-week6-day7-closeout.md`。
- 更早记录：见 `docs/archive/implementation_log/`。

## Week 7 Day 1 Repo Scanner 准备状态

- 当前阶段仍是 Week 7 Day 1，`RepoScanner.scan(root)` 尚未开始实现。
- 当前任务入口：`docs/02_DAILY_TASKS.md`；唯一实时状态与下一指令：`docs/09_NEXT_ACTIONS.md`。
- 计划边界：只读授权 workspace，忽略 `.git` / `__pycache__` / `.venv`，限制文件资源，不执行 shell 或网络。

## 2026-07-12：P0 shell wrapper fail-closed 修复

### 本次完成

- 按已批准的最小 ASK 方案，将 `cmd`、`powershell`、`pwsh` 及其 `.exe`、大小写、完整路径形式统一分类为 `ASK/shell_wrapper`。
- permission gate 在 wrapper 路径返回 approval-required，摘要审计记录 `executed=false`，fake runtime 不会被调用。
- permission 示例把安全路径改为直接执行 Python 版本查询，并新增 wrapper ASK 输出，避免把 wrapper 误当作安全示例。

### TDD 与验证证据

- RED：wrapper 分类/gate/safety 新测试最初为 `11 failed, 18 passed`；补充完整路径引号用例后，聚焦分类测试为 `8 failed`。
- GREEN：wrapper 三层回归为 `30 passed`；permission/shell 相关回归为 `59 passed`；示例相关聚焦回归为 `31 passed`。
- 全量：`E:\python\Scripts\pytest.exe -q` 为 `218 passed, 1 skipped`。
- 真实示例：`examples/01_minimal_agent.py` 至 `05_checkpoint_rollback.py` 五个示例均退出码为 0。
- 编译：沙箱内因既有 `__pycache__` 写权限失败；批准后在沙箱外执行 `E:\python\python.exe -m compileall src examples -q`，退出码为 0。

### 能力边界

- 已关闭已知 shell wrapper 默认落入 `SAFE` 的 P0 路径。
- 尚未实现内部命令、嵌套 wrapper、编码命令、动态字符串或 shell AST 的语义解析；这些能力不得从本修复推导。

## 2026-07-12：P1 稳定非法输入错误修复

- `ToolRegistry.run(...)` 对 list、dict、`None`、空值与空白名称返回 `INVALID_ARGUMENT`，保留 trace，并统一记录到 `<invalid-tool-name>`；合法未知名称仍返回 `UNKNOWN_TOOL`。
- `ApprovalRequest` / `ApprovalDecision` 现在先校验字符串类型和空白，再校验严格 bool、timezone-aware datetime 与时间关系；工厂方法和 `is_expired(...)` 复用同一契约。
- TDD RED：ToolRegistry 为 `5 failed, 1 passed`；approval 为 `11 failed, 9 passed`。初始 GREEN 为 `6 passed` 与 `20 passed`。
- 独立评审发现并补测非法 trace、保留统计键碰撞和 DST fold；补强后 tools 为 `48 passed`、approval 为 `21 passed`，相关 tools/approval/retry/AgentLoop 回归为 `81 passed`。
- 全量为 `243 passed, 1 skipped`；5 个示例均退出码 0；compileall 沙箱外重跑退出码 0。
- 边界：F-02/F-03 已关闭；audit 生命周期、approval resume、lint/type-check/CI 不在本切片。

## 2026-07-11：文档、协作记忆与模块审计

### 本次完成

- 新增 `docs/18_IMPLEMENTED_MODULE_FLOWS.md`，用源码与测试证据整理真实模块调用链和工程作用，并标注“部分实现/未接入主链”边界。
- 新增 `docs/19_CODE_COMPLETION_AUDIT_2026-07-10.md`，记录代码完成度审计快照、证据、风险与整改建议。
- 同步 `docs/15_MEMORY_SYSTEM.md`、`DOC_RULES.md` 和 `docs/INDEX.md`，完善仓库协作记忆治理、冲突裁决、文档职责和导航。
- 同步 `README.md`、`ARCHITECTURE.md` 与工业级差距台账，使项目入口、真实架构和缺口描述与当前源码证据一致。
- 将 Week 6 Day 1-Day 7 的独有实现证据归入同一历史 archive，并压缩活跃日志。

### 验证与边界

- 本轮是文档、协作记忆与模块审计维护，未修改 Python 代码、测试或面试题归档状态。
- Week 7 Day 1、`RepoScanner` 尚未开始及既有测试基线保持不变。
- 审计提出的代码整改尚未实施，等待用户批准后再进入单独实现切片。
