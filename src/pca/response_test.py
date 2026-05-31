import json
import os
from openai import OpenAI

# 1. 初始化客户端 (请确保环境中已配置 OPENAI_API_KEY)
client = OpenAI(api_key="sk-hk9gzEKb90U3g4AtnpytApL7qtS1zhTknMzyA54xkkqHROcM",
                base_url="https://api.bianxie.ai/v1")

def inspect_response_structure():
    print("正在调用 Responses API 发起请求...\n")

    # 2. 使用 Responses API 发起请求
    response = client.responses.create(
        model="gpt-5.4",
        input="请用一句话解释什么是 AI Agent，并假装调用一个天气工具。"
    )

    # ==========================================
    # 核心视角 1：查看完整的原始 JSON 结构
    # ==========================================
    print("=== 1. 完整的 Response JSON 结构 ===")
    # 提示：使用 model_dump_json() 是查看底层数据结构的最佳实践
    # 它会清晰展示 id, object, created_at, model 以及 output 列表
    print(response.model_dump_json(indent=2))
    print("\n" + "=" * 50 + "\n")

    # ==========================================
    # 核心视角 2：便捷提取最终文本
    # ==========================================
    print("=== 2. 快捷文本输出 (response.output_text) ===")
    # 官方 SDK 提供的辅助属性，直接提取最终的自然语言回复
    print(response.output_text)
    print("\n" + "=" * 50 + "\n")

    # # ==========================================
    # # 核心视角 3：解构 Agent 的输出项 (Items)
    # # ==========================================
    # print("=== 3. 遍历解析 Output Items (Agent 开发的核心) ===")
    # # 在复杂的 Agent 工作流中，模型可能会同时输出推理过程、工具调用和文本。
    # # 遍历 response.output 是最权威且健壮的处理方式。
    # for index, item in enumerate(response.output):
    #     print(f"[{index}] 发现 Item，类型 (type): {item.type}")
    #
    #     if item.type == "message":
    #         print(f"    - 角色 (role): {item.role}")
    #         print(f"    - 状态 (status): {item.status}")
    #         # 深入解析 message 内部的 content 块
    #         for block in item.content:
    #             if block.type == "output_text":
    #                 print(f"    - 文本内容: {block.text}")
    #
    #     elif item.type == "reasoning":
    #         print("    - 这是一个推理节点，包含模型在得出结论前的思考过程。")
    #
    #     elif item.type == "function_call":
    #         print(f"    - 命中工具调用！工具名称 (name): {item.name}")
    #         print(f"    - 调用 ID (call_id): {item.call_id}")
    #         # 注意：arguments 是 JSON 字符串，需要反序列化
    #         args_dict = json.loads(item.arguments)
    #         print(f"    - 解析后的参数 (arguments): {args_dict}")
    #
    #     else:
    #         print(f"    - 未知或未处理的 Item 类型: {item.type}")
    #     print("-" * 30)


if __name__ == "__main__":
    inspect_response_structure()