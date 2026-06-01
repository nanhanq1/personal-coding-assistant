import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pca.core.agent_loop import AgentLoop
from pca.core.messages import Message, ToolCall
from pca.core.mock_llm import ScriptedLLM
from pca.tools.base import Tool
from pca.tools.registry import ToolRegistry


def main() -> None:
    """Run the Day 1 minimal Agent Loop demo."""

    llm = ScriptedLLM(
        responses=[
            Message(
                role="assistant",
                content="I should call the echo tool.",
                tool_calls=[ToolCall(name="echo", arguments={"text": "hello"})],
            ),
            Message(role="assistant", content="The tool said: hello"),
        ]
    )

    tool = Tool(
        name="echo",
        description="回显工具",
        handler=lambda arguments: arguments.get("text", ""),
    )
    tool_registry = ToolRegistry()
    tool_registry.register(tool)
    loop = AgentLoop(
        llm=llm,
        tools=tool_registry,
    )

    result = loop.run("Say hello")
    for message in result.messages:
        label = message.role if message.name is None else f"{message.role}:{message.name}"
        print(f"{label}: {message.content}")


if __name__ == "__main__":
    main()
