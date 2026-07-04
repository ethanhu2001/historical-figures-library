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


def parse_figure(text: str, slug: str) -> Figure:
    text = text.strip()
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"{slug}: expected a top-level '# Name' heading")
    name = lines[0][2:].strip()

    worldview = _section(lines[1:], "worldview")
    if worldview is None:
        raise ValueError(f"{slug}: missing required '## Worldview' section")

    return Figure(slug=slug, name=name, worldview=worldview, system_prompt=text)


def _section(lines: list[str], heading_name: str) -> str | None:
    body: list[str] = []
    found = False
    in_section = False
    for line in lines:
        match = _SECTION_RE.match(line)
        if match:
            if in_section:
                break
            in_section = match.group(1).strip().lower() == heading_name
            found = found or in_section
            continue
        if in_section:
            body.append(line)
    return "\n".join(body).strip() if found else None


def _parse_figure_file(path: Path) -> Figure:
    return parse_figure(path.read_text(encoding="utf-8"), slug=path.stem)


def load_figures(figures_dir: Path = FIGURES_DIR) -> list[Figure]:
    figures = []
    for path in sorted(figures_dir.glob("*.md")):
        if path.stem == "TEMPLATE":
            continue
        figures.append(_parse_figure_file(path))
    return figures
