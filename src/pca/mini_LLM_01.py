import json
import os
import subprocess
from operator import truediv
from typing import Any

from openai import OpenAI

from src.pca.response_test import client

Client = OpenAI(
    api_key="sk-hk9gzEKb90U3g4AtnpytApL7qtS1zhTknMzyA54xkkqHROcM",
    base_url="https://api.bianxie.ai/v1"
)

tools = [
    {
        "type":"function",
        "name":"run_bash",
        "description":"Run a bash command",
        "parameters":{
            "type":"object",
            "properties":{
                "command":{
                    "type":"string",
                    "description":"The bash command to run"
                }
            },
            "required":["command"],
            "additionalProperties": False
        },
        "strict": True
    }
]

def run_bash(command: str) -> str:
    """
    Execute a shell command.

    这只是教学版防护，不是生产级 sandbox。
    真实 Coding Agent 应该使用 Docker / VM / sandbox / 权限审批。
    """

    dangerous_patterns = [
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
    ]

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
            timeout=120,
        )

        output = (result.stdout + result.stderr).strip()

        if not output:
            output = "(no output)"

        if result.returncode != 0:
            output = f"[exit code: {result.returncode}]\n{output}"

        return output[:50000]

    except subprocess.TimeoutExpired:
        return "Error: Timeout after 120 seconds."

    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def call_function(name, args):
    if name == "run_bash":
        command = args.get("command")
        if not isinstance(command, str) or not command.strip():
            return "Error: Missing or invalid command."

        print(f"\033[33m$ {command}\033[0m")
        output = run_bash(command)
        print(output[:1000])

        return output

    return f"Error: Unknown function: {name}"


def agent_loop(input_list:list[dict[str:any]]):
    """
    OpenAI Responses API Agent Loop.

    核心流程：

    1. client.responses.create(...)
    2. 检查 response.output
    3. 如果有 function_call，执行本地工具
    4. 把 function_call_output 追加回 input_list
    5. 继续循环
    6. 如果没有 function_call，返回 response.output_text
    """
    max_steps = 20

    for step in range(max_steps):
        response = Client.responses.create(
            model="gpt-5.4",
            input=input_list,
            tools=tools
        )

        output_message = response.output

        input_list += output_message

        function_calls = [
            item for item in response.output
            if getattr(item, "type", None) == "function_call"
        ]

        if not function_calls:
            return response.output_text or ""

        for item in function_calls:
            name = item.name
            raw_args = item.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError as e:
                output = (
                    "Error: Invalid JSON arguments from model.\n"
                    f"JSON error: {e}\n"
                    f"Raw arguments: {raw_args}"
                )
            else:
                output = call_function(name, args)

            input_list.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": output
            })

    return "Error: Agent loop exceeded max_steps."

if __name__ == "__main__":
    print("s01: OpenAI Responses API Agent Loop")
    print("输入问题，回车发送。输入 q / exit / 空行 退出。\n")

    input_list: list[dict[str, Any]] = []

    while True:
        try:
            query = input("\033[36ms01-responses >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query.strip().lower() in ("q", "exit", ""):
            break

        input_list.append(
            {
                "role": "user",
                "content": query,
            }
        )

        final_text = agent_loop(input_list)

        if final_text:
            print("\n\033[32mAssistant:\033[0m")
            print(final_text)

        print()