from __future__ import annotations

from unittest.mock import MagicMock, patch

from council.llm import DEFAULT_MODEL, Citation, LLMClient


def test_init_uses_explicit_api_key_over_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    with patch("council.llm.anthropic.Anthropic") as mock_anthropic:
        LLMClient(api_key="explicit-key")

    mock_anthropic.assert_called_once_with(api_key="explicit-key")


def test_init_falls_back_to_environment_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    with patch("council.llm.anthropic.Anthropic") as mock_anthropic:
        LLMClient(api_key=None)

    mock_anthropic.assert_called_once_with(api_key="env-key")


def test_complete_sends_model_system_messages_and_max_tokens():
    with patch("council.llm.anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(type="text", text="hello", citations=None)]
        )
        client = LLMClient(api_key="k")

        client.complete(system="sys", messages=[{"role": "user", "content": "hi"}], max_tokens=50)

    mock_client.messages.create.assert_called_once_with(
        model=DEFAULT_MODEL,
        system="sys",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=50,
    )


def test_complete_forwards_tools_when_given():
    with patch("council.llm.anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(type="text", text="hello", citations=None)]
        )
        client = LLMClient(api_key="k")
        tools = [{"type": "web_search_20250305", "name": "web_search"}]

        client.complete(
            system="sys", messages=[{"role": "user", "content": "hi"}], tools=tools
        )

    mock_client.messages.create.assert_called_once_with(
        model=DEFAULT_MODEL,
        system="sys",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=1024,
        tools=tools,
    )


def test_complete_joins_only_text_content_blocks():
    with patch("council.llm.anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = MagicMock(
            content=[
                MagicMock(type="text", text="Hello, ", citations=None),
                MagicMock(type="tool_use", text="ignored"),
                MagicMock(type="text", text="world.", citations=None),
            ]
        )
        client = LLMClient(api_key="k")

        reply = client.complete(system="sys", messages=[{"role": "user", "content": "hi"}])

    assert reply.text == "Hello, world."


def test_complete_extracts_citations_from_cited_text_blocks():
    citation = MagicMock(url="https://example.com/a", title="Example Article")
    with patch("council.llm.anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(type="text", text="A claim.", citations=[citation])]
        )
        client = LLMClient(api_key="k")

        reply = client.complete(system="sys", messages=[{"role": "user", "content": "hi"}])

    assert reply.citations == [Citation(url="https://example.com/a", title="Example Article")]
