from __future__ import annotations

from council.figure import Figure
from council.llm import LLMClient

MIN_FIGURES = 3

CONVENER_SYSTEM_PROMPT = """You are the Convener of a Council of historical figures. \
You do not argue a Worldview of your own — your job is to orchestrate the debate: \
choose which Council members are relevant to a question, decide who speaks next and \
why, judge when a debate has run its course, and write the closing Synthesis. On \
factual or logical disputes, state plainly which claims held up under challenge. On \
genuinely value-laden questions, do not force a winner — present the strongest \
surviving form of each side."""


class Convener:
    def __init__(self, llm: LLMClient, council: list[Figure]) -> None:
        self.llm = llm
        self.council = council

    def _ask(self, system: str, prompt: str, max_tokens: int) -> str:
        return self.llm.complete(
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )

    def prompt_figure(self, figure: Figure, transcript: str) -> str:
        prompt = (
            f"{_transcript_block(transcript)}"
            "Speak now. If you need information from the user to make your case, "
            "wrap your question in <clarifying_question></clarifying_question> "
            "tags instead of responding normally."
        )
        return self._ask(system=figure.system_prompt, prompt=prompt, max_tokens=1200)

    def select_figures(self, question: str) -> list[Figure]:
        roster_desc = "\n".join(
            f"- {f.name}: {f.worldview.splitlines()[0]}" for f in self.council
        )
        prompt = (
            f"Question: {question}\n\n"
            f"Council roster:\n{roster_desc}\n\n"
            f"Select at least {MIN_FIGURES} Council members whose Worldview is "
            "genuinely relevant to this question. Reply with ONLY a comma-separated "
            "list of their exact names, nothing else."
        )
        reply = self._ask(system=CONVENER_SYSTEM_PROMPT, prompt=prompt, max_tokens=200)
        by_name = _figures_by_name(self.council)
        selected = []
        for token in reply.split(","):
            figure = by_name.get(token.strip().casefold())
            if figure and figure not in selected:
                selected.append(figure)
        if len(selected) < MIN_FIGURES:
            remaining = [f for f in self.council if f not in selected]
            selected += remaining[: MIN_FIGURES - len(selected)]
        return selected

    def choose_next_speaker(self, seated: list[Figure], transcript: str) -> Figure | None:
        roster_desc = ", ".join(f.name for f in seated)
        prompt = (
            f"Seated Council members: {roster_desc}\n\n"
            f"{_transcript_block(transcript)}"
            "Who should speak next? If the debate has run its course, reply with "
            "exactly END instead of a name. Reply with ONLY the figure's exact "
            "name (or END), nothing else."
        )
        reply = self._ask(system=CONVENER_SYSTEM_PROMPT, prompt=prompt, max_tokens=100)
        decoded = reply.strip().casefold()
        if decoded == "end":
            return None
        by_name = _figures_by_name(seated)
        return by_name.get(decoded, seated[0])

    def synthesize(self, transcript: str) -> str:
        prompt = (
            f"{_transcript_block(transcript)}"
            "Write the closing Synthesis: state which factual or logical claims "
            "held up under challenge, and for any genuinely value-laden "
            "disagreement, present the strongest surviving version of each side "
            "rather than forcing a winner."
        )
        return self._ask(system=CONVENER_SYSTEM_PROMPT, prompt=prompt, max_tokens=2000)


def _transcript_block(transcript: str) -> str:
    return f"Transcript so far:\n{transcript}\n\n"


def _figures_by_name(figures: list[Figure]) -> dict[str, Figure]:
    return {f.name.strip().casefold(): f for f in figures}
