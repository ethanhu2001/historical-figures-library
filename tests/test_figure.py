from __future__ import annotations

from pathlib import Path

import pytest

from council.figure import load_figures, parse_figure

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def test_loads_all_figures_excluding_template():
    figures = load_figures(FIGURES_DIR)
    slugs = {f.slug for f in figures}
    assert "TEMPLATE" not in slugs
    md_files_excluding_template = [p for p in FIGURES_DIR.glob("*.md") if p.stem != "TEMPLATE"]
    assert len(figures) == len(md_files_excluding_template)


def test_each_figure_has_worldview_and_full_system_prompt():
    for figure in load_figures(FIGURES_DIR):
        assert figure.worldview.strip()
        assert figure.name in figure.system_prompt
        assert "## Debate behavior" in figure.system_prompt


def test_parse_figure_extracts_name_and_worldview_from_text():
    text = (
        "# Test Figure\n\n"
        "## Worldview\n\n"
        "Believes in testing.\n\n"
        "## Biography\n\n"
        "Some bio, discarded.\n"
    )

    figure = parse_figure(text, slug="test-figure")

    assert figure.slug == "test-figure"
    assert figure.name == "Test Figure"
    assert figure.worldview == "Believes in testing."
    assert figure.system_prompt == text.strip()


def test_parse_figure_raises_when_missing_name_heading():
    text = "Not a heading\n\n## Worldview\n\nSomething.\n"

    with pytest.raises(ValueError):
        parse_figure(text, slug="bad")


def test_parse_figure_raises_when_missing_worldview_section():
    text = "# Test Figure\n\n## Biography\n\nSome bio.\n"

    with pytest.raises(ValueError):
        parse_figure(text, slug="bad")
