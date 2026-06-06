"""Responses API tool-calling 学习实验。

这是早期教学脚本，不属于当前 Day 4 的正式 AgentLoop 主路径。
保留它的目的，是让你以后对照真实 Responses API 的 function_call 流程。
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from pca.response_test import create_client


# 修改前旧代码（API key 已脱敏）：
# from openai import OpenAI
# from src.pca.response_test import client
# Client = OpenAI(
#     api_key="<REDACTED_API_KEY>",
#     base_url="https://api.bianxie.ai/v1",
# )
#
# 问题：硬编码密钥、错误的 src.pca 导入、导入模块时立即创建真实 client。
Client = None

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "run_bash",
        "description": "Run a bash command in the current teaching workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to run",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


def run_bash(command: str) -> str:
    """执行教学版 shell 命令。

    这里只是学习 Responses API 工具调用格式，不是生产级 sandbox。
    正式 Coding Agent 应该走 `ShellRuntime`、权限审批、审计日志和后续 sandbox。
    """
    # 修改前旧代码：
    # normalized = command.strip().lower()
    #
    # 问题：没有先确认 command 是非空字符串，坏参数会触发 AttributeError。
    if not isinstance(command, str) or command.strip() == "":
        return "Error: Missing or invalid command."

    dangerous_patterns = (
        "rm -rf /",
        "rm -rf ~",
        "rm -rf *",
        "sudo",
        "shutdown",
        "reboot",
        "mkfs",
        "dd if=",
        ":(){",
        "> /dev/",
        "chmod -R 777 /",
        "chown -R",
        "curl | sh",
        "wget | sh",
    )
    normalized = command.strip().lower()
    if any(pattern in normalized for pattern in dangerous_patterns):
        return "Error: Dangerous command blocked."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            # 修改前旧代码：
            # timeout=120,
            #
            # 问题：实验脚本直接给 120 秒，学习阶段等待成本过高。
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "Error: Timeout after 30 seconds."
    except OSError as exc:
        return f"Error: {exc}"

    output = (result.stdout + result.stderr).strip() or "(no output)"
    if result.returncode != 0:
        output = f"[exit code: {result.returncode}]\n{output}"
    return output[:10000]


def call_function(name: str, args: dict[str, Any]) -> str:
    """根据 Responses API 返回的 function_call 分发到本地函数。"""
    if name != "run_bash":
        return f"Error: Unknown function: {name}"

    command = args.get("command")
    if not isinstance(command, str) or not command.strip():
        return "Error: Missing or invalid command."

    print(f"\033[33m$ {command}\033[0m")
    output = run_bash(command)
    print(output[:1000])
    return output


def agent_loop(input_list: list[dict[str, Any]]) -> str:
    """运行一个教学版 Responses API Agent Loop。

    核心流程：
    1. 调用 `client.responses.create(...)`。
    2. 检查 `response.output` 中是否包含 `function_call`。
    3. 本地执行工具，把 `function_call_output` 追加回输入。
    4. 继续循环，直到模型返回最终文本或超过最大步数。
    """
    if not isinstance(input_list, list):
        raise TypeError("input_list must be a list")

    # 修改前旧代码：
    # response = Client.responses.create(
    #     model="gpt-5.4",
    #     input=input_list,
    #     tools=tools
    # )
    #
    # 问题：依赖导入时创建的全局 Client，且模型名和工具变量都硬编码在函数内部路径上。
    active_client = create_client()
    model = os.environ.get("PCA_OPENAI_MODEL", "gpt-4.1-mini")
    max_steps = 20

    for _ in range(max_steps):
        response = active_client.responses.create(
            model=model,
            input=input_list,
            tools=TOOLS,
        )

        output_items = list(response.output)
        input_list += output_items

        function_calls = [
            item
            for item in output_items
            if getattr(item, "type", None) == "function_call"
        ]

        if not function_calls:
            return response.output_text or ""

        for item in function_calls:
            raw_args = item.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError as exc:
                output = (
                    "Error: Invalid JSON arguments from model.\n"
                    f"JSON error: {exc}\n"
                    f"Raw arguments: {raw_args}"
                )
            else:
                output = call_function(item.name, args)

            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": output,
                }
            )

    return "Error: Agent loop exceeded max_steps."


if __name__ == "__main__":
    print("s01: OpenAI Responses API Agent Loop")
    print("输入问题，回车发送。输入 q / exit / 空行 退出。\n")

    history: list[dict[str, Any]] = []
    while True:
        try:
            query = input("\033[36ms01-responses >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        final_text = agent_loop(history)
        if final_text:
            print("\n\033[32mAssistant:\033[0m")
            print(final_text)
        print()
