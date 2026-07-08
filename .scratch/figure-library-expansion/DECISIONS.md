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

---

## 2026-07-07: Resolve manual-selection design + finish the Council rename

**Decision**: Resolved both items left open above.
1. Manual pick **constrains the candidate set**, it does not bypass the
   Convener. `Convener.select_figures(question, candidates=None)` now takes
   an optional `candidates` param; when given, relevance judgment (and the
   `MIN_FIGURES` top-up fallback) runs only over that narrowed pool instead
   of `self.library`. This means a manual pick still needs to satisfy
   `MIN_FIGURES = 3` — the same floor applies whether the pool is the full
   Library or a user-narrowed one, since the floor is about debate dynamics
   (enough distinct Worldviews to make a debate, not a Q&A), not about how
   the pool was assembled.
2. CLI surface is an **interactive picker**: `council ask` always offers a
   numbered Library listing before the debate starts, prompting for a
   comma-separated pick (validated to be exactly one number per Figure and
   at least `MIN_FIGURES`) or an empty Enter to skip straight to full
   automatic Convener selection. No separate flag-based path — one prompt
   covers both "narrow it myself" and "let the Convener pick," so a single
   command teaches the whole feature rather than requiring the user to
   discover a flag.

Also finished the deferred renames flagged in the 2026-07-04 entry:
- `Convener.__init__`'s `council` param/attribute is now `library`.
- `CONVENER_SYSTEM_PROMPT` and the prompt strings inside `select_figures` /
  `choose_next_speaker` now say Library/Cabinet instead of Council — this
  changes what's actually sent to the model, not just docs.
- `Convener.needs_council` renamed to `needs_debate` — it was never really
  asking "does this need the Council," it's asking "does this question
  call for a debate at all," and the old name baked in the retired term.
- `ROSTER.md` renamed to `LIBRARY.md`; `council roster` CLI command renamed
  to `council library` to match.
- The `council` Python package/CLI command name is still deliberately left
  alone (brand name, per the prior entry) — only the `roster` subcommand
  was renamed, since that one was about content, not the product name.

**Why**: The interactive-picker choice (over a `--figures` flag) trades a
little friction on every `ask` call for discoverability — with a flag,
first-time users would never learn manual selection exists unless they read
docs; a prompt teaches the feature by just running the command. The
constrain-not-bypass choice keeps `select_figures`'s existing relevance +
top-up logic as the single code path for both automatic and manual
selection — a manual pick is just a smaller `pool` argument, not a second
implementation to maintain and keep in sync.

**What it changes**:
- `src/council/convener.py`: `library` param/attribute, `needs_debate`
  rename, `candidates` param on `select_figures`, prompt text.
- `src/council/session.py`: `Session.run` takes an optional
  `pick_candidates` callback (mirrors the existing `ask_user`/`on_turn`
  callback pattern), called only when a debate is actually needed (i.e.
  not for trivial questions that skip straight to `answer_directly`), and
  its result is forwarded as `candidates` to `select_figures`.
- `src/council/cli.py`: `_pick_candidates` implements the interactive
  numbered picker; `council roster` renamed to `council library`.
- `LIBRARY.md` (renamed from `ROSTER.md`), `README.md`: reflect the above.
- `tests/test_convener.py`, `tests/test_session.py`,
  `tests/test_transcript.py`, `tests/test_figure.py`: updated for the
  renames, plus new coverage for `candidates` constraining `select_figures`
  and for `pick_candidates` being forwarded / skipped correctly.
  `test_figure.py`'s figure-count assertion was hardcoded at 7 and started
  failing as new Figure files landed from the content-expansion thread
  proceeding in parallel — replaced with a count derived from
  `figures/*.md` on disk so it no longer needs updating as the Library
  grows.

**Not yet done**:
- No CLI-level test exists for `_pick_candidates` (exercised manually and
  via `Session`/`Convener` unit tests instead) — this repo has no
  `test_cli.py` precedent yet; adding one is a reasonable follow-up once
  the CLI surface has more than two commands.
- User story 9 ("clear whether a Session used hand-picked or automatic
  selection") is only satisfied at the point of picking — `_pick_candidates`
  echoes which mode was chosen before the debate starts, but nothing in the
  transcript or Synthesis records it after the fact. Revisit if transcripts
  need to be self-describing later.
