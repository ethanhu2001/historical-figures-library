from __future__ import annotations

import typer
from dotenv import load_dotenv

from council.convener import MIN_FIGURES, Convener
from council.figure import Figure, load_figures
from council.llm import LLMClient
from council.session import Session
from council.transcript import save_transcript

load_dotenv()

app = typer.Typer(help="Convene a Cabinet to debate a question.")


def _pick_candidates(figures: list[Figure]) -> list[Figure] | None:
    typer.echo()
    typer.echo(typer.style("Library:", bold=True))
    for i, figure in enumerate(figures, start=1):
        typer.echo(f"  {i}. {figure.name} — {figure.worldview.splitlines()[0]}")

    while True:
        raw = typer.prompt(
            f"\nPick Figures for this Cabinet by number, comma-separated (at least "
            f"{MIN_FIGURES}), or press Enter to let the Convener auto-select from the "
            "full Library",
            default="",
            show_default=False,
        )
        if not raw.strip():
            typer.echo("Auto-selecting Cabinet from the full Library.")
            return None

        try:
            picks = [figures[int(token.strip()) - 1] for token in raw.split(",")]
        except (ValueError, IndexError):
            typer.echo("Could not parse that — enter comma-separated numbers from the list above.")
            continue

        if len(picks) < MIN_FIGURES:
            typer.echo(f"Pick at least {MIN_FIGURES} Figures, or press Enter to skip.")
            continue

        typer.echo(f"Cabinet narrowed to your picks: {', '.join(f.name for f in picks)}")
        return picks


@app.command()
def ask(question: str) -> None:
    """Ask a question and watch the Cabinet debate it."""
    figures = load_figures()
    convener = Convener(llm=LLMClient(), library=figures)
    session = Session(question=question, convener=convener)

    def ask_user(prompt: str) -> str:
        typer.echo()
        typer.echo(typer.style(f"[Clarifying question] {prompt}", fg=typer.colors.YELLOW))
        return typer.prompt("Your answer")

    def on_turn(speaker: str, text: str) -> None:
        typer.echo()
        typer.echo(typer.style(f"{speaker}:", bold=True))
        typer.echo(text)

    result = session.run(
        ask_user=ask_user,
        on_turn=on_turn,
        pick_candidates=lambda: _pick_candidates(figures),
    )

    label = "Synthesis:" if session.seated else "Answer:"
    typer.echo()
    typer.echo(typer.style(label, bold=True, fg=typer.colors.CYAN))
    typer.echo(result)

    path = save_transcript(session)
    typer.echo()
    typer.echo(f"Transcript saved to {path}")


@app.command()
def library() -> None:
    """List the Library of available Figures."""
    for figure in load_figures():
        typer.echo(f"- {figure.name}")


if __name__ == "__main__":
    app()
