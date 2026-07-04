from __future__ import annotations

from council.llm import Completion


class FakeLLM:
    def __init__(self, replies):
        self._replies = iter(replies)

    def complete(self, system, messages, max_tokens=1024, tools=None):
        return Completion(text=next(self._replies))
