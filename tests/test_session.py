from __future__ import annotations

import itertools

from council.figure import Figure
from council.session import ROUNDS_PER_FIGURE, Session


class FakeLLM:
    def __init__(self, replies):
        self._replies = iter(replies)

    def complete(self, system, messages, max_tokens=1024):
        return next(self._replies)


class FakeConvener:
    """Bypasses real Convener parsing so Session's own loop logic — turn
    budget, clarifying-question pausing, recording — can be tested in
    isolation."""

    def __init__(self, seated, speaker_sequence, llm, synthesis="Synthesis text"):
        self.seated = seated
        self._speaker_sequence = iter(speaker_sequence)
        self.llm = llm
        self._synthesis = synthesis

    def select_figures(self, question):
        return self.seated

    def choose_next_speaker(self, seated, transcript):
        return next(self._speaker_sequence)

    def synthesize(self, transcript):
        return self._synthesis


def figure(name):
    return Figure(slug=name.lower(), name=name, worldview="w", system_prompt=f"# {name}")


def test_normal_debate_ends_when_convener_says_end():
    a, b = figure("A"), figure("B")
    convener = FakeConvener(
        seated=[a, b],
        speaker_sequence=[a, b, None],
        llm=FakeLLM(["reply from A", "reply from B"]),
    )
    session = Session(question="Q?", convener=convener)

    synthesis = session.run(ask_user=lambda p: "unused")

    assert synthesis == "Synthesis text"
    speakers = [t.speaker for t in session.turns]
    assert speakers == ["User", "A", "B", "Convener (Synthesis)"]


def test_clarifying_question_pauses_and_does_not_count_against_turn_budget():
    a = figure("A")
    convener = FakeConvener(
        seated=[a],
        speaker_sequence=[a, a, None],
        llm=FakeLLM(
            [
                "<clarifying_question>What's your risk tolerance?</clarifying_question>",
                "final reply from A",
            ]
        ),
    )
    session = Session(question="Q?", convener=convener)
    asked = []

    def ask_user(prompt):
        asked.append(prompt)
        return "high risk"

    session.run(ask_user=ask_user)

    assert asked == ["(A) What's your risk tolerance?"]
    speakers = [t.speaker for t in session.turns]
    assert speakers == ["User", "A", "User", "A", "Convener (Synthesis)"]


def test_debate_stops_at_turn_budget_even_if_convener_never_ends():
    a, b = figure("A"), figure("B")
    convener = FakeConvener(
        seated=[a, b],
        speaker_sequence=itertools.cycle([a, b]),
        llm=FakeLLM(itertools.repeat("plain reply")),
    )
    session = Session(question="Q?", convener=convener)

    session.run(ask_user=lambda p: "unused")

    expected_max_turns = ROUNDS_PER_FIGURE * len([a, b])
    figure_turns = [t for t in session.turns if t.speaker in ("A", "B")]
    assert len(figure_turns) == expected_max_turns
