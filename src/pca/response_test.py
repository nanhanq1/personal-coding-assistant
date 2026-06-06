"""Responses API 结构观察实验。

这个文件仍然保留为学习脚本，但不能在导入时创建真实 API client。
真实密钥必须来自环境变量，避免把个人凭据写进源码或提交到仓库。
"""

from __future__ import annotations

import os
from typing import Any


client = None


def create_client() -> Any:
    """按需创建 OpenAI client；缺少依赖或密钥时给出清晰错误。"""
    # 修改前旧代码（API key 已脱敏）：
    # from openai import OpenAI
    # client = OpenAI(
    #     api_key="<REDACTED_API_KEY>",
    #     base_url="https://api.bianxie.ai/v1",
    # )
    #
    # 问题：源码硬编码密钥，并且模块导入时立即创建真实 API client。
    api_key = os.environ.get("PCA_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 PCA_OPENAI_API_KEY 或 OPENAI_API_KEY 环境变量")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("请先安装 openai SDK 后再运行此实验脚本") from exc

    base_url = os.environ.get("PCA_OPENAI_BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def inspect_response_structure() -> None:
    """调用 Responses API 并打印原始结构，帮助学习 output items。"""
    active_client = create_client()
    model = os.environ.get("PCA_OPENAI_MODEL", "gpt-4.1-mini")

    print("正在调用 Responses API 发起请求...\n")
    response = active_client.responses.create(
        model=model,
        input="请用一句话解释什么是 AI Agent，并假装调用一个天气工具。",
    )

    print("=== 1. 完整的 Response JSON 结构 ===")
    print(response.model_dump_json(indent=2))
    print("\n" + "=" * 50 + "\n")

    print("=== 2. 快捷文本输出 (response.output_text) ===")
    print(response.output_text)


if __name__ == "__main__":
    inspect_response_structure()
