"""测试早期 API 实验代码不会污染正式包的安全边界。"""

import importlib
from pathlib import Path


def test_source_code_does_not_contain_hardcoded_api_keys():
    """测试正式源码中不能硬编码 sk- 形态的 API key。"""
    repo_root = Path(__file__).resolve().parents[1]
    source_files = [
        path
        for path in (repo_root / "src").rglob("*.py")
        if "__pycache__" not in path.parts
    ]

    leaked_files = [
        path.relative_to(repo_root).as_posix()
        for path in source_files
        if "sk-" in path.read_text(encoding="utf-8")
    ]

    assert leaked_files == []


def test_response_experiment_import_has_no_required_api_dependency():
    """测试实验模块导入时不创建真实 API client，也不要求 OpenAI SDK 必须安装。"""
    module = importlib.import_module("pca.response_test")

    assert hasattr(module, "inspect_response_structure")
    assert getattr(module, "client", None) is None


def test_responses_agent_experiment_import_has_no_required_api_dependency():
    """测试 Agent 实验模块导入时不会读取硬编码密钥或创建真实 API client。"""
    module = importlib.import_module("pca.mini_LLM_01")

    assert hasattr(module, "agent_loop")
    assert getattr(module, "Client", None) is None
