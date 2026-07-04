from __future__ import annotations

import os
from dataclasses import dataclass, field

import anthropic

DEFAULT_MODEL = "claude-opus-4-8"


@dataclass(frozen=True)
class Citation:
    url: str
    title: str


@dataclass(frozen=True)
class Completion:
    text: str
    citations: list[Citation] = field(default_factory=list)


class LLMClient:
    """Thin wrapper around the Anthropic client so Figure/Convener code
    doesn't touch the SDK directly — keeps a future provider swap contained
    here, per ADR-0001."""

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None) -> None:
        self.model = model
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    def complete(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
    ) -> Completion:
        kwargs = {"tools": tools} if tools is not None else {}
        response = self._client.messages.create(
            model=self.model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs,
        )
        text_blocks = [block for block in response.content if block.type == "text"]
        text = "".join(block.text for block in text_blocks)
        citations = [
            Citation(url=citation.url, title=citation.title)
            for block in text_blocks
            for citation in (block.citations or [])
        ]
        return Completion(text=text, citations=citations)
