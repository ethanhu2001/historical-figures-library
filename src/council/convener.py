from __future__ import annotations

from typing import TypeVar

from council.figure import Figure
from council.llm import Completion, LLMClient

T = TypeVar("T")
_MISSING = object()

MIN_FIGURES = 3
MAX_SEARCHES_PER_TURN = 3

# Anthropic's server-side web search tool: Claude decides when to search and
# the API executes it, returning results in the same response. `max_uses`
# caps searches for this one call, i.e. for one Figure's turn.
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": MAX_SEARCHES_PER_TURN,
}

CONVENER_SYSTEM_PROMPT = """You are the Convener, drawing on a Library of historical figures. \
You do not argue a Worldview of your own — your job is to orchestrate the debate: \
choose which Figures form the Cabinet for a question, decide who speaks next and \
why, judge when a debate has run its course, and write the closing Synthesis. On \
factual or logical disputes, state plainly which claims held up under challenge. On \
genuinely value-laden questions, do not force a winner — present the strongest \
surviving form of each side."""


class Convener:
    def __init__(self, llm: LLMClient, library: list[Figure]) -> None:
        self.llm = llm
        self.library = library

    def _ask(
        self, system: str, prompt: str, max_tokens: int, tools: list[dict] | None = None
    ) -> Completion:
        return self.llm.complete(
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            tools=tools,
        )

    def _ask_choice(self, prompt: str, valid: dict[str, T], max_tokens: int) -> T:
        """Ask for a reply drawn from a small closed vocabulary (e.g. yes/no, or
        a seated Figure's name/END) and resolve it to the matching value.
        Raises UnrecognizedReply if the normalized reply matches no key."""
        reply = self._ask(system=CONVENER_SYSTEM_PROMPT, prompt=prompt, max_tokens=max_tokens).text
        value = valid.get(reply.strip().casefold(), _MISSING)
        if value is _MISSING:
            raise UnrecognizedReply(reply, valid_keys=list(valid))
        return value

    def prompt_figure(self, figure: Figure, transcript: str) -> Completion:
        prompt = (
            f"{_transcript_block(transcript)}"
            "Speak now. If you need information from the user to make your case, "
            "wrap your question in <clarifying_question></clarifying_question> "
            "tags instead of responding normally."
        )
        return self._ask(
            system=figure.system_prompt,
            prompt=prompt,
            max_tokens=1200,
            tools=[WEB_SEARCH_TOOL],
        )

    def needs_debate(self, question: str) -> bool:
        prompt = (
            f"Question: {question}\n\n"
            "Does this genuinely call for a debate among historical figures with "
            "different worldviews (a decision, a value-laden tradeoff, a matter of "
            "opinion or strategy)? Reply NO instead if it's a simple factual or "
            "trivial question with one straightforward answer (e.g. the weather, "
            "a definition, basic arithmetic) that would not benefit from debate.\n\n"
            "Reply with ONLY YES or NO, nothing else."
        )
        try:
            return self._ask_choice(prompt, valid={"yes": True, "no": False}, max_tokens=10)
        except UnrecognizedReply:
            return False

    def answer_directly(self, question: str) -> str:
        prompt = f"Question: {question}\n\nAnswer directly and concisely."
        return self._ask(
            system="You are a helpful, direct assistant. Answer plainly, without "
            "adopting any persona.",
            prompt=prompt,
            max_tokens=500,
        ).text

    def select_figures(
        self, question: str, candidates: list[Figure] | None = None
    ) -> list[Figure]:
        pool = self.library if candidates is None else candidates
        roster_desc = "\n".join(f"- {f.name}: {f.worldview.splitlines()[0]}" for f in pool)
        prompt = (
            f"Question: {question}\n\n"
            f"Library:\n{roster_desc}\n\n"
            f"Select at least {MIN_FIGURES} Figures to form a Cabinet whose Worldview is "
            "genuinely relevant to this question. Reply with ONLY a comma-separated "
            "list of their exact names, nothing else."
        )
        reply = self._ask(system=CONVENER_SYSTEM_PROMPT, prompt=prompt, max_tokens=200).text
        by_name = _figures_by_name(pool)
        selected = []
        for token in reply.split(","):
            figure = by_name.get(token.strip().casefold())
            if figure and figure not in selected:
                selected.append(figure)
        if len(selected) < MIN_FIGURES:
            remaining = [f for f in pool if f not in selected]
            selected += remaining[: MIN_FIGURES - len(selected)]
        return selected

    def choose_next_speaker(self, seated: list[Figure], transcript: str) -> Figure | None:
        roster_desc = ", ".join(f.name for f in seated)
        prompt = (
            f"Seated Cabinet: {roster_desc}\n\n"
            f"{_transcript_block(transcript)}"
            "Who should speak next? If the debate has run its course, reply with "
            "exactly END instead of a name. Reply with ONLY the figure's exact "
            "name (or END), nothing else."
        )
        valid: dict[str, Figure | None] = {**_figures_by_name(seated), "end": None}
        return self._ask_choice(prompt, valid=valid, max_tokens=100)

    def synthesize(self, transcript: str) -> str:
        prompt = (
            f"{_transcript_block(transcript)}"
            "Write the closing Synthesis: state which factual or logical claims "
            "held up under challenge, and for any genuinely value-laden "
            "disagreement, present the strongest surviving version of each side "
            "rather than forcing a winner."
        )
        return self._ask(system=CONVENER_SYSTEM_PROMPT, prompt=prompt, max_tokens=2000).text


def _transcript_block(transcript: str) -> str:
    return f"Transcript so far:\n{transcript}\n\n"


def _figures_by_name(figures: list[Figure]) -> dict[str, Figure]:
    return {f.name.strip().casefold(): f for f in figures}


class UnrecognizedReply(Exception):
    def __init__(self, reply: str, valid_keys: list[str]) -> None:
        super().__init__(f"Convener reply {reply!r} matched none of {valid_keys}")
        self.reply = reply
        self.valid_keys = valid_keys


class UnknownFigure(Exception):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"{identifier!r} does not match any Figure in the Library")
        self.identifier = identifier


class TooFewFigures(Exception):
    def __init__(self, given: int, required: int = MIN_FIGURES) -> None:
        super().__init__(f"Cabinet needs at least {required} distinct Figures, got {given}")
        self.given = given
        self.required = required


def resolve_picks(identifiers: list[str], library: list[Figure]) -> list[Figure]:
    """Resolve user-picked Figure names/slugs into a validated Cabinet candidate
    pool. Raises UnknownFigure the moment an identifier doesn't match the
    Library, and TooFewFigures if fewer than MIN_FIGURES distinct Figures
    remain after de-duplication."""
    by_name = _figures_by_name(library)
    resolved: dict[str, Figure] = {}
    for identifier in identifiers:
        figure = by_name.get(identifier.strip().casefold())
        if figure is None:
            raise UnknownFigure(identifier)
        resolved[figure.slug] = figure
    if len(resolved) < MIN_FIGURES:
        raise TooFewFigures(given=len(resolved))
    return list(resolved.values())
