from __future__ import annotations

from collections.abc import Sequence

from pca.core.messages import Message


class ScriptedLLM:
    """用于测试和早期示例的确定性 LLM adapter。"""

    def __init__(self, responses: Sequence[Message]):
        # 修改前旧代码：
        # self._responses = list(responses)
        # self._index = 0
        #
        # 问题：测试脚本可以传入字符串或非 Message 对象，失败会延迟到 AgentLoop 内部。
        if not isinstance(responses, Sequence) or isinstance(responses, (str, bytes)):
            raise TypeError("responses must be a sequence of Message objects")
        if any(not isinstance(response, Message) for response in responses):
            raise TypeError("responses must contain Message objects")

        self._responses = list(responses)
        self._index = 0

    def complete(self, messages: list[Message]) -> Message:
        """返回下一条脚本化响应；脚本耗尽时直接暴露测试配置错误。"""
        # 修改前旧代码：
        # if self._index >= len(self._responses):
        #     raise RuntimeError("ScriptedLLM has no response left.")
        #
        # 问题：没有校验传入的 messages 是否仍是 Message 列表。
        if not isinstance(messages, list) or any(not isinstance(message, Message) for message in messages):
            raise TypeError("messages must be a list of Message objects")

        if self._index >= len(self._responses):
            raise RuntimeError("ScriptedLLM has no response left.")
        response = self._responses[self._index]
        self._index += 1
        return response
