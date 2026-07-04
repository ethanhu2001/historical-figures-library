from __future__ import annotations


class FakeLLM:
    def __init__(self, replies):
        self._replies = iter(replies)

    def complete(self, system, messages, max_tokens=1024):
        return next(self._replies)
