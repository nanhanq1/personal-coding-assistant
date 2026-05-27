from __future__ import annotations

from collections.abc import Sequence

from src.pca.core.messages import Message


class ScriptedLLM:
    """A deterministic LLM adapter used for tests and early examples."""

    def __init__(self, responses: Sequence[Message]):
        self._responses = list(responses)
        self._index = 0

    def complete(self, messages: list[Message]) -> Message:
        """Return the next scripted response and fail when the script is exhausted."""

        if self._index >= len(self._responses):
            raise RuntimeError("ScriptedLLM has no response left.")
        response = self._responses[self._index]
        self._index += 1
        return response

