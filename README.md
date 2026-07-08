# Historical Figures Library

[![GitHub](https://img.shields.io/badge/GitHub-ethanhu2001%2Fhistorical--figures--library-181717?logo=github)](https://github.com/ethanhu2001/historical-figures-library)

A Library of historical figures, each an AI agent with its own `.md` system
prompt and a distinct Worldview. Ask a question and the Convener assembles a
Cabinet from the Library to debate it — they don't just answer, they argue
with each other. See `CONTEXT.md` for the full vocabulary (Library, Cabinet,
Figure, Convener, Session, Synthesis) and `docs/adr/` for why the system is
shaped the way it is.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # then fill in ANTHROPIC_API_KEY
```

## Usage

```bash
council ask "Should I take a lower-paying job with more autonomy?"
council library
```

Each Session:

1. `council ask` shows you the full Library and lets you pick at least 3
   Figures for the Cabinet yourself — or press Enter to let the Convener
   auto-select relevant Figures from the Library instead.
2. Figures debate — the Convener names who speaks next and why, each turn.
   Any Figure can pause the Session with a clarifying question for you.
3. Debate ends when the Convener judges it's run its course, or after
   `5 × number of seated Figures` turns, whichever comes first.
4. The Convener writes a closing Synthesis and the full transcript is saved
   to `sessions/`.

## Adding a Figure

Copy `figures/TEMPLATE.md`, fill in the five sections, and add a row to
`LIBRARY.md`. See `docs/agents/domain.md` for how domain terms and ADRs are
maintained in this repo.

## Tests

```bash
pytest
```
