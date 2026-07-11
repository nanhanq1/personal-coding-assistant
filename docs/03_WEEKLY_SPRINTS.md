# Weekly Sprints

本文件保留活跃 Sprint 入口。完整 24 周计划见 `docs/14_24_WEEK_PLAN.md`。

## Sprint 共同原则

- 每周交付一个可运行、可测试、可验收的能力切片。
- 每周至少覆盖一个失败路径或安全边界。
- 每周同步测试、文档、实现日志、下一步行动和面试题状态。
- 文档不能宣称源码没有实现的能力。

## 当前 Sprint：Week 7 - Repo Scanner / Repo Map

Week 6 已完成带边界收口：permission、audit、workspace、checkpoint/rollback、safety、E2E 和 trace metadata 已有证据；结构化 observability、自动 retry、审批恢复和跨副作用 rollback 仍明确保留在 gap ledger 中。

### 1. 本周主题

代码库理解入口：从授权根目录生成稳定、可预算、不会泄漏 ignored 文件的 repo inventory 和 repo map。

### 2. 工业级目标

- 扫描范围受 workspace 和资源上限约束。
- 忽略 `.git`、`__pycache__`、`.venv` 等噪声目录。
- 文件清单排序稳定、输出可测试、后续可扩展到语言识别和摘要。

### 3. 核心概念

- file inventory
- ignore rules
- language detection
- summary budget

### 4. 参考项目与资料

- Aider Repo Map：https://aider.chat/docs/repomap.html
- mini-SWE-agent：https://github.com/SWE-agent/mini-swe-agent
- Git ignore：https://git-scm.com/docs/gitignore

### 5. 代码模块

- `src/pca/coding/repo_scanner.py`
- `src/pca/coding/repo_map.py`
- `src/pca/coding/file_summary.py`

### 6. 每日安排

| Day | 学习目标 | 代码任务 | 测试任务 | 文档任务 | 完成标准 |
|---|---|---|---|---|---|
| 1 | 文件清单 | `RepoScanner.scan(root)` | ignore/size/boundary | ADR 草稿 | scanner 通过 |
| 2 | 语言识别 | suffix/language metadata | py/md/toml | notes | metadata 通过 |
| 3 | 文件摘要 | `FileSummary` | summary tests | docs | summary 通过 |
| 4 | Repo map | `RepoMap.build` | stable order | Mermaid | map 通过 |
| 5 | Budget | max files/max chars | truncation | eval note | 超预算语义明确 |
| 6 | 示例 | `examples/06_repo_map.py` | example test | README | 示例可运行 |
| 7 | 复盘 | 小重构 | 全量测试 | 面试题 | 放行 |

### 7. 共同安全边界

- 不扫描 workspace 外目录。
- 不读取 ignored 文件内容。
- 不执行 shell、网络或写盘副作用。
- 预算或权限失败时 fail-closed，并返回可解释错误。
