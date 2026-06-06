# 2026-06-06 修改前代码快照

这个目录保留本次工业级加固前的 `src/`、`tests/` 和 `examples/`，用于和当前代码做对比。

安全说明：旧版 `src/pca/mini_LLM_01.py` 和 `src/pca/response_test.py` 中出现过硬编码 API key。为了避免在备份目录中重复保存敏感凭据，快照里的该字面量已替换为 `<REDACTED_API_KEY>`，其他逻辑保持用于审查对比。
