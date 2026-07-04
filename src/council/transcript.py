from __future__ import annotations

import datetime
import re
from pathlib import Path

from council.paths import REPO_ROOT
from council.session import Session

SESSIONS_DIR = REPO_ROOT / "sessions"


def _slugify(text: str, max_words: int = 8) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "-".join(words[:max_words]) or "session"


def save_transcript(session: Session, sessions_dir: Path = SESSIONS_DIR) -> Path:
    sessions_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.date.today().isoformat()
    slug = _slugify(session.question)
    path = sessions_dir / f"{date}-{slug}.md"

    lines = [f"# {session.question}", "", f"Seated: {', '.join(f.name for f in session.seated)}", ""]
    for turn in session.turns:
        lines += [f"## {turn.speaker}", "", turn.text, ""]
        if turn.citations:
            sources = ", ".join(f"[{c.title}]({c.url})" for c in turn.citations)
            lines += [f"Sources: {sources}", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
