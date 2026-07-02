# Historical Figures Library

A Council of historical figures, each an AI agent with its own `.md` system
prompt and a distinct Worldview, who debate the questions you bring them —
they don't just answer, they argue with each other. See `CONTEXT.md` for
the full vocabulary (Council, Figure, Convener, Session, Synthesis) and
`docs/adr/` for why the system is shaped the way it is.

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
council roster
```

Each Session:

1. The Convener reads your question and seats at least 3 relevant Figures
   from the roster (`ROSTER.md`).
2. Figures debate — the Convener names who speaks next and why, each turn.
   Any Figure can pause the Session with a clarifying question for you.
3. Debate ends when the Convener judges it's run its course, or after
   `5 × number of seated Figures` turns, whichever comes first.
4. The Convener writes a closing Synthesis and the full transcript is saved
   to `sessions/`.

## Adding a Figure

Copy `figures/TEMPLATE.md`, fill in the five sections, and add a row to
`ROSTER.md`. See `docs/agents/domain.md` for how domain terms and ADRs are
maintained in this repo.

## Tests

```bash
pytest
```
