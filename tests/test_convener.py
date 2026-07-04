from __future__ import annotations

from council.convener import MIN_FIGURES, Convener
from council.figure import Figure
from fakes import FakeLLM


def make_figures(*names):
    return [
        Figure(slug=n.lower().replace(" ", "-"), name=n, worldview="w", system_prompt="p")
        for n in names
    ]


def test_select_figures_parses_comma_separated_names():
    council = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio", "Charlie Munger")
    convener = Convener(llm=FakeLLM(["Marcus Aurelius, Warren Buffett, Ray Dalio"]), council=council)

    selected = convener.select_figures("Should I take this job?")

    assert [f.name for f in selected] == ["Marcus Aurelius", "Warren Buffett", "Ray Dalio"]


def test_select_figures_tops_up_to_minimum_when_reply_is_short():
    council = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio", "Charlie Munger")
    convener = Convener(llm=FakeLLM(["Marcus Aurelius"]), council=council)

    selected = convener.select_figures("A narrow question")

    assert len(selected) == MIN_FIGURES
    assert selected[0].name == "Marcus Aurelius"


def test_select_figures_does_not_substring_match_a_shorter_name():
    council = make_figures("Lee", "Lee Kuan Yew", "Warren Buffett", "Ray Dalio")
    convener = Convener(
        llm=FakeLLM(["Lee Kuan Yew, Warren Buffett, Ray Dalio"]), council=council
    )

    selected = convener.select_figures("Should I take this job?")

    assert [f.name for f in selected] == ["Lee Kuan Yew", "Warren Buffett", "Ray Dalio"]


def test_choose_next_speaker_returns_none_on_end():
    council = make_figures("Marcus Aurelius", "Warren Buffett")
    convener = Convener(llm=FakeLLM(["END"]), council=council)

    assert convener.choose_next_speaker(council, "transcript") is None


def test_choose_next_speaker_matches_named_figure():
    council = make_figures("Marcus Aurelius", "Warren Buffett")
    convener = Convener(llm=FakeLLM(["Warren Buffett"]), council=council)

    speaker = convener.choose_next_speaker(council, "transcript")

    assert speaker.name == "Warren Buffett"


def test_choose_next_speaker_does_not_substring_match_a_shorter_name():
    council = make_figures("Lee", "Lee Kuan Yew")
    convener = Convener(llm=FakeLLM(["Lee Kuan Yew"]), council=council)

    speaker = convener.choose_next_speaker(council, "transcript")

    assert speaker.name == "Lee Kuan Yew"


def test_prompt_figure_sends_figures_system_prompt_and_transcript():
    figure = make_figures("Marcus Aurelius")[0]
    figure = Figure(
        slug=figure.slug, name=figure.name, worldview="w", system_prompt="Marcus's system prompt"
    )
    seen = {}

    class RecordingLLM:
        def complete(self, system, messages, max_tokens=1024):
            seen["system"] = system
            seen["prompt"] = messages[0]["content"]
            return "reply from Marcus"

    convener = Convener(llm=RecordingLLM(), council=[figure])

    reply = convener.prompt_figure(figure, "User: Should I take this job?")

    assert reply == "reply from Marcus"
    assert seen["system"] == "Marcus's system prompt"
    assert "User: Should I take this job?" in seen["prompt"]
