from __future__ import annotations

from pathlib import Path

from council.figure import load_figures

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def test_loads_all_figures_excluding_template():
    figures = load_figures(FIGURES_DIR)
    slugs = {f.slug for f in figures}
    assert "TEMPLATE" not in slugs
    assert len(figures) == 7


def test_each_figure_has_worldview_and_full_system_prompt():
    for figure in load_figures(FIGURES_DIR):
        assert figure.worldview.strip()
        assert figure.name in figure.system_prompt
        assert "## Debate behavior" in figure.system_prompt
