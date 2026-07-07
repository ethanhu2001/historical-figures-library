# Design decisions: figure-library-expansion

Running log of architectural decisions made while building this PRD (see
`PRD.md`). Scope is architecture only — terminology, selection-layer design,
CLI surface — not individual content choices (which figures, sourcing).

Once this PRD ships, distill this log into an ADR under `docs/adr/` and
remove this file.

## Format

Each entry: date, the decision, the reasoning, and what it changes.

---

## 2026-07-04: Retire "Council," split into "Library" and "Cabinet"

**Decision**: `CONTEXT.md`'s **Council** term (the full curated assembly) is
retired. Two new terms replace it:
- **Library** — the full pool of every available Figure. Loosely curated
  (must meet `TEMPLATE.md`'s quality bar) but not hand-picked for
  fame/balance the way the old Council was.
- **Cabinet** — the ≥3 Figures actually seated for one Session, drawn from
  the Library either by the Convener's automatic relevance judgment or by
  the user's manual pick.

Retirement is total, not just internal to the glossary: user-facing copy
(README, CLI help text, `figures/TEMPLATE.md`) was updated too, not just
kept as brand language, since the old term was actively misleading once the
pool grows past a hand-picked handful.

**Why**: `CONTEXT.md` had a latent contradiction — Council was defined as
the whole available pool, but `Session`'s own definition already used
"the Council convening to debate one question" to mean the specific
per-question group, not the whole roster. That reading breaks once the pool
is dozens of Figures instead of 7. Splitting into Library (the pool) and
Cabinet (the per-Session subset) resolves the contradiction and matches how
`Session` already talked about itself, so `Session`'s definition needed only
a light reword, not a rewrite.

**What it changes**:
- `CONTEXT.md`: Council entry removed; Library and Cabinet entries added;
  Worldview, Convener, and Session entries reworded to reference them.
- `README.md`, `figures/TEMPLATE.md`, `src/council/cli.py` (Typer help
  text and command docstrings only): "Council" language replaced.
- **Not yet done** (deferred to implementation, since these are code/prompt
  changes rather than glossary decisions):
  - `Convener.__init__`'s `council` param/attribute (`src/council/convener.py`)
    conceptually is now "the Library" — rename pending.
  - `CONVENER_SYSTEM_PROMPT` and the prompt strings built inside
    `select_figures`/`choose_next_speaker` (`"Council roster:"`,
    `"Select at least N Council members"`, `"Seated Council members:"`)
    still say "Council" — this is the actual text sent to the model, so
    changing it is a behavior change, not just docs.
  - The `council` Python package name and `council` CLI command itself were
    deliberately left alone — treated as the product/brand name (like a
    company name), not the retired glossary term. Flagging in case that's
    not the intent.
  - `ROSTER.md`'s filename — still named after the retired term; rename is
    tied to the still-open CLI-naming question below.

**Still open** (not yet resolved in this pass):
1. How manual Figure selection interacts with `Convener.select_figures`
   (full bypass vs. constrains the candidate set) and whether the
   `MIN_FIGURES = 3` floor applies to a manual pick.
2. CLI surface: fate of `council roster` / `ROSTER.md` under the new
   Library term, and the shape of a manual-pick flag on `council ask`.
