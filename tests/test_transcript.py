from __future__ import annotations

from council.convener import Convener
from council.llm import Citation
from council.session import Session, Turn
from council.transcript import save_transcript


def test_save_transcript_renders_citations_under_a_turn(tmp_path):
    session = Session(question="Q?", convener=Convener(llm=None, library=[]))
    session.turns = [
        Turn(
            speaker="A",
            text="A grounded claim.",
            citations=[Citation(url="https://example.com", title="Example")],
        )
    ]

    path = save_transcript(session, sessions_dir=tmp_path)

    content = path.read_text(encoding="utf-8")
    assert "Sources:" in content
    assert "[Example](https://example.com)" in content
