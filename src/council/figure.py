from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

FIGURES_DIR = Path(__file__).resolve().parent.parent.parent / "figures"

_SECTION_RE = re.compile(r"^##\s+(.+)$")


@dataclass(frozen=True)
class Figure:
    slug: str
    name: str
    worldview: str
    system_prompt: str


def _parse_figure_file(path: Path) -> Figure:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"{path}: expected a top-level '# Name' heading")
    name = lines[0][2:].strip()

    sections: dict[str, str] = {}
    heading: str | None = None
    body: list[str] = []
    for line in lines[1:]:
        match = _SECTION_RE.match(line)
        if match:
            if heading is not None:
                sections[heading] = "\n".join(body).strip()
            heading = match.group(1).strip().lower()
            body = []
        else:
            body.append(line)
    if heading is not None:
        sections[heading] = "\n".join(body).strip()

    if "worldview" not in sections:
        raise ValueError(f"{path}: missing required '## Worldview' section")

    return Figure(
        slug=path.stem,
        name=name,
        worldview=sections["worldview"],
        system_prompt=text,
    )


def load_figures(figures_dir: Path = FIGURES_DIR) -> list[Figure]:
    figures = []
    for path in sorted(figures_dir.glob("*.md")):
        if path.stem == "TEMPLATE":
            continue
        figures.append(_parse_figure_file(path))
    return figures
