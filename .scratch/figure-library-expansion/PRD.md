Status: ready-for-agent

# Figure library expansion + user-facing selection

## Problem Statement

The Council currently has 7 curated Figures (`ROSTER.md`). The user wants a
much larger library of historical figures to draw from, scoped initially to
their own taste — Chinese and American history — rather than the small,
hand-picked set that exists today. With a small roster, the Convener's
automatic selection (ADR-0001: pick ≥3 relevant Figures before a Session
starts) is sufficient. With a large library, the user also wants to be able
to pick Figures for a Session themselves, rather than always leaving it to
automatic selection.

## Solution

1. Grow the library of Figure system prompts well beyond the current 7,
   starting with Chinese and American historical figures, each following the
   existing `figures/TEMPLATE.md` structure (Worldview, Biography, Speaking
   style, Known positions, Debate behavior).
2. Add a user-facing selection layer so the user can browse the full library
   and choose specific Figures for a Session themselves, as an alternative
   (or complement) to the Convener's automatic relevance-based selection.

## User Stories

1. As a user, I want a large library of historical figures spanning Chinese and American history, so I have far more Worldviews to draw from than the current 7.
2. As a user who likes Chinese history, I want figures spanning multiple eras/schools of thought (not just modern reform-era figures like Deng Xiaoping), so the library reflects real breadth.
3. As a user who likes American history, I want a similarly broad set of American figures across eras and domains (not just business figures like Buffett/Munger/Rockefeller).
4. As a user, I want each new Figure to follow the same template and quality bar as existing ones, so voice and rigor stay consistent as the library grows.
5. As a user, I want to browse/list the full library (distinct from whatever subset is "active" for a Session), so I know who's available before I ask a question.
6. As a user, I want to explicitly select specific Figures for a Session, so I control who debates my question instead of relying solely on the Convener's automatic pick.
7. As a user, I want the option to skip manual selection and let the Convener auto-select from the full library, so I'm not forced to pick every time.
8. As a user, I want to search or filter the library (e.g. by nationality, era, or Worldview), so picking from a large list is still fast.
9. As a user, I want it to be clear whether a Session used my hand-picked Figures or the Convener's automatic selection, so I understand who I'm hearing from and why.
10. As a maintainer, I want an efficient way to draft many new Figure files (e.g. AI-assisted drafting against `TEMPLATE.md`) rather than hand-authoring dozens of files one at a time.

## Implementation Decisions

Resolved (see `DECISIONS.md` for full reasoning):

- **"Council" vs "Library" terminology** (2026-07-04): Council is retired.
  **Library** is the full pool of every available Figure; **Cabinet** is the
  ≥3 Figures seated for one Session, drawn from the Library. `CONTEXT.md`,
  `README.md`, `figures/TEMPLATE.md`, `ROSTER.md` (renamed `LIBRARY.md`),
  and all Convener-facing code/prompts have been updated accordingly.
- **Interaction with ADR-0001** (2026-07-07): manual selection **constrains
  the candidate set** passed to `Convener.select_figures` rather than
  bypassing it or existing as a fully separate path — the Convener's
  existing relevance-judgment and `MIN_FIGURES` top-up logic runs unchanged
  over whatever pool it's given. `MIN_FIGURES = 3` applies to a manual pick
  the same as to automatic selection.
- **CLI surface** (2026-07-07): `council ask` always offers an interactive
  numbered Library picker before the debate starts (pick ≥3 by number, or
  press Enter to let the Convener auto-select from the full Library). No
  separate flag. `council roster` renamed to `council library`.

Still open:

- **Content sourcing for new Figures**: needs a decision on process for
  drafting each new Figure's Worldview/Biography/Known positions accurately
  (research process, review step) versus just generating plausible-sounding
  content — accuracy matters more here than for the selection-layer
  plumbing. (Content drafting is already underway in parallel — see
  `LIBRARY.md` for the current roster — but this process question is not
  yet formally decided.)

## Testing Decisions

- New Figure `.md` files are content, not code — validate them the way `tests/test_figure.py` already validates `load_figures()` (e.g. required sections present, parses correctly), not via bespoke per-figure tests.
- Any manual-selection CLI/Convener changes should be tested at the same seam as `tests/test_convener.py` (Convener behavior), asserting on the resulting selected-Figures set rather than CLI output text.

## Out of Scope

- Automatic fact-checking or sourcing citations for Figure content.
- Figures outside Chinese and American history (explicitly out of scope for this pass — the user set this scope deliberately based on personal taste; broadening nationality coverage is a future decision, not this one).
- Any change to the core debate mechanics (Session/turn-taking/Clarifying Questions) beyond how Figures for a Session get selected.

## Further Notes

This is a two-part feature: content work (writing many new Figure files) and
a small architecture decision (Council/Library terminology + selection UI).
The content work can proceed incrementally and in parallel once the roster
question is settled, whereas the selection layer needs the terminology/ADR
question resolved first since it changes what `Convener.select_figures` is
selecting *from*.
