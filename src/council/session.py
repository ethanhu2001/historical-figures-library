from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from council.convener import Convener
from council.figure import Figure

ROUNDS_PER_FIGURE = 5

# Implementation convention (not a grilled design decision): a Figure signals
# a Clarifying Question by wrapping it in this tag instead of responding
# normally. Simplest thing that works without full tool-use schemas per Figure.
CLARIFYING_QUESTION_RE = re.compile(
    r"<clarifying_question>(.*?)</clarifying_question>", re.IGNORECASE | re.DOTALL
)

AskUser = Callable[[str], str]
OnTurn = Callable[[str, str], None]


@dataclass
class Turn:
    speaker: str
    text: str


@dataclass
class Session:
    question: str
    convener: Convener
    turns: list[Turn] = field(default_factory=list)
    seated: list[Figure] = field(default_factory=list)

    def transcript_text(self) -> str:
        return "\n\n".join(f"{t.speaker}: {t.text}" for t in self.turns)

    def run(self, ask_user: AskUser, on_turn: OnTurn | None = None) -> str:
        self.seated = self.convener.select_figures(self.question)
        self._record("User", self.question, on_turn)

        max_turns = ROUNDS_PER_FIGURE * len(self.seated)
        debate_turns = 0

        while debate_turns < max_turns:
            speaker = self.convener.choose_next_speaker(self.seated, self.transcript_text())
            if speaker is None:
                break

            reply = self.convener.prompt_figure(speaker, self.transcript_text())
            clarifying = CLARIFYING_QUESTION_RE.search(reply)

            if clarifying:
                self._record(speaker.name, reply, on_turn)
                answer = ask_user(f"({speaker.name}) {clarifying.group(1).strip()}")
                self._record("User", answer, on_turn)
                continue  # Clarifying pauses don't count against the turn budget

            self._record(speaker.name, reply, on_turn)
            debate_turns += 1

        synthesis = self.convener.synthesize(self.transcript_text())
        self._record("Convener (Synthesis)", synthesis, on_turn)
        return synthesis

    def _record(self, speaker: str, text: str, on_turn: OnTurn | None) -> None:
        self.turns.append(Turn(speaker=speaker, text=text))
        if on_turn:
            on_turn(speaker, text)
