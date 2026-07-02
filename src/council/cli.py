from __future__ import annotations

import typer
from dotenv import load_dotenv

from council.convener import Convener
from council.figure import load_figures
from council.llm import LLMClient
from council.session import Session
from council.transcript import save_transcript

load_dotenv()

app = typer.Typer(help="Convene the Council to debate a question.")


@app.command()
def ask(question: str) -> None:
    """Ask the Council a question and watch them debate it."""
    figures = load_figures()
    convener = Convener(llm=LLMClient(), council=figures)
    session = Session(question=question, convener=convener)

    def ask_user(prompt: str) -> str:
        typer.echo()
        typer.echo(typer.style(f"[Clarifying question] {prompt}", fg=typer.colors.YELLOW))
        return typer.prompt("Your answer")

    def on_turn(speaker: str, text: str) -> None:
        typer.echo()
        typer.echo(typer.style(f"{speaker}:", bold=True))
        typer.echo(text)

    synthesis = session.run(ask_user=ask_user, on_turn=on_turn)

    typer.echo()
    typer.echo(typer.style("Synthesis:", bold=True, fg=typer.colors.CYAN))
    typer.echo(synthesis)

    path = save_transcript(session)
    typer.echo()
    typer.echo(f"Transcript saved to {path}")


@app.command()
def roster() -> None:
    """List the current Council roster."""
    for figure in load_figures():
        typer.echo(f"- {figure.name}")


if __name__ == "__main__":
    app()
