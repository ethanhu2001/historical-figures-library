from __future__ import annotations

import pytest

from council.convener import MIN_FIGURES, Convener, TooFewFigures, UnknownFigure, resolve_picks
from council.figure import Figure
from council.llm import Completion
from fakes import FakeLLM


def make_figures(*names):
    return [
        Figure(slug=n.lower().replace(" ", "-"), name=n, worldview="w", system_prompt="p")
        for n in names
    ]


def test_needs_debate_is_true_on_yes_reply():
    convener = Convener(llm=FakeLLM(["YES"]), library=[])

    assert convener.needs_debate("Should I take this job?") is True


def test_needs_debate_is_false_on_no_reply():
    convener = Convener(llm=FakeLLM(["NO"]), library=[])

    assert convener.needs_debate("What is the weather like?") is False


def test_answer_directly_returns_llm_text():
    convener = Convener(llm=FakeLLM(["It's sunny."]), library=[])

    assert convener.answer_directly("What is the weather like?") == "It's sunny."


def test_select_figures_parses_comma_separated_names():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio", "Charlie Munger")
    convener = Convener(llm=FakeLLM(["Marcus Aurelius, Warren Buffett, Ray Dalio"]), library=library)

    selected = convener.select_figures("Should I take this job?")

    assert [f.name for f in selected] == ["Marcus Aurelius", "Warren Buffett", "Ray Dalio"]


def test_select_figures_tops_up_to_minimum_when_reply_is_short():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio", "Charlie Munger")
    convener = Convener(llm=FakeLLM(["Marcus Aurelius"]), library=library)

    selected = convener.select_figures("A narrow question")

    assert len(selected) == MIN_FIGURES
    assert selected[0].name == "Marcus Aurelius"


def test_select_figures_does_not_substring_match_a_shorter_name():
    library = make_figures("Lee", "Lee Kuan Yew", "Warren Buffett", "Ray Dalio")
    convener = Convener(
        llm=FakeLLM(["Lee Kuan Yew, Warren Buffett, Ray Dalio"]), library=library
    )

    selected = convener.select_figures("Should I take this job?")

    assert [f.name for f in selected] == ["Lee Kuan Yew", "Warren Buffett", "Ray Dalio"]


def test_select_figures_is_constrained_to_passed_candidates_not_full_library():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio", "Charlie Munger")
    candidates = [f for f in library if f.name != "Charlie Munger"]
    convener = Convener(llm=FakeLLM(["Charlie Munger, Marcus Aurelius"]), library=library)

    selected = convener.select_figures("Should I take this job?", candidates=candidates)

    assert "Charlie Munger" not in [f.name for f in selected]


def test_select_figures_tops_up_from_candidates_not_full_library():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio", "Charlie Munger")
    candidates = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio")
    convener = Convener(llm=FakeLLM(["Marcus Aurelius"]), library=library)

    selected = convener.select_figures("A narrow question", candidates=candidates)

    assert len(selected) == MIN_FIGURES
    assert "Charlie Munger" not in [f.name for f in selected]


def test_resolve_picks_maps_names_to_figures():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio")

    resolved = resolve_picks(["Marcus Aurelius", "Ray Dalio", "Warren Buffett"], library)

    assert [f.name for f in resolved] == ["Marcus Aurelius", "Ray Dalio", "Warren Buffett"]


def test_resolve_picks_does_not_substring_match_a_shorter_name():
    library = make_figures("Lee", "Lee Kuan Yew", "Warren Buffett")

    resolved = resolve_picks(["Lee Kuan Yew", "Warren Buffett", "Lee"], library)

    assert [f.name for f in resolved] == ["Lee Kuan Yew", "Warren Buffett", "Lee"]


def test_resolve_picks_raises_unknown_figure_for_an_unmatched_identifier():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio")

    with pytest.raises(UnknownFigure):
        resolve_picks(["Marcus Aurelius", "Someone Not In The Library", "Ray Dalio"], library)


def test_resolve_picks_raises_too_few_figures_below_the_minimum():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio")

    with pytest.raises(TooFewFigures):
        resolve_picks(["Marcus Aurelius", "Warren Buffett"], library)


def test_resolve_picks_deduplicates_before_checking_the_minimum():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio")

    with pytest.raises(TooFewFigures):
        resolve_picks(["Marcus Aurelius", "Marcus Aurelius", "Marcus Aurelius"], library)


def test_resolve_picks_deduplicates_repeated_identifiers():
    library = make_figures("Marcus Aurelius", "Warren Buffett", "Ray Dalio")

    resolved = resolve_picks(
        ["Marcus Aurelius", "Warren Buffett", "Marcus Aurelius", "Ray Dalio"], library
    )

    assert [f.name for f in resolved] == ["Marcus Aurelius", "Warren Buffett", "Ray Dalio"]


def test_choose_next_speaker_returns_none_on_end():
    library = make_figures("Marcus Aurelius", "Warren Buffett")
    convener = Convener(llm=FakeLLM(["END"]), library=library)

    assert convener.choose_next_speaker(library, "transcript") is None


def test_choose_next_speaker_matches_named_figure():
    library = make_figures("Marcus Aurelius", "Warren Buffett")
    convener = Convener(llm=FakeLLM(["Warren Buffett"]), library=library)

    speaker = convener.choose_next_speaker(library, "transcript")

    assert speaker.name == "Warren Buffett"


def test_choose_next_speaker_does_not_substring_match_a_shorter_name():
    library = make_figures("Lee", "Lee Kuan Yew")
    convener = Convener(llm=FakeLLM(["Lee Kuan Yew"]), library=library)

    speaker = convener.choose_next_speaker(library, "transcript")

    assert speaker.name == "Lee Kuan Yew"


def test_choose_next_speaker_raises_when_reply_does_not_match_a_seated_figure():
    library = make_figures("Marcus Aurelius", "Warren Buffett")
    convener = Convener(llm=FakeLLM(["Someone Not On The Council"]), library=library)

    with pytest.raises(ValueError):
        convener.choose_next_speaker(library, "transcript")


def test_prompt_figure_sends_figures_system_prompt_and_transcript():
    figure = make_figures("Marcus Aurelius")[0]
    figure = Figure(
        slug=figure.slug, name=figure.name, worldview="w", system_prompt="Marcus's system prompt"
    )
    seen = {}

    class RecordingLLM:
        def complete(self, system, messages, max_tokens=1024, tools=None):
            seen["system"] = system
            seen["prompt"] = messages[0]["content"]
            seen["tools"] = tools
            return Completion(text="reply from Marcus")

    convener = Convener(llm=RecordingLLM(), library=[figure])

    reply = convener.prompt_figure(figure, "User: Should I take this job?")

    assert reply.text == "reply from Marcus"
    assert seen["system"] == "Marcus's system prompt"
    assert "User: Should I take this job?" in seen["prompt"]
    assert seen["tools"] is not None
