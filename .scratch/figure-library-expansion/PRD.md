Status: needs-triage

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

Open — flagged for a design pass before this is `ready-for-agent`:

- **"Council" vs "Library" terminology**: `CONTEXT.md` currently defines **Council** as "the full assembly of Figure agents available to participate in debates... membership is curated." Growing to a large library changes that meaning. Needs a domain-modeling pass (this repo has a `domain-modeling` / `ubiquitous-language` skill for exactly this) to decide: does "Council" become the large pool, with a new term for a per-Session subset? Or does "Library" become the large pool and "Council" stays the smaller curated/eligible set? This affects `ROSTER.md`, `CONTEXT.md`, and `docs/adr/0001-convener-orchestrated-debate.md`.
- **Interaction with ADR-0001**: the Convener currently auto-selects ≥3 relevant Figures from the whole roster (`Convener.select_figures` in `src/council/convener.py`). A manual selection layer needs a decision on whether it fully replaces that call for a given Session, constrains its input set, or is offered as an alternate path — this is a real architectural choice, not a detail.
- **CLI surface**: likely a `council library` (or renamed) listing command distinct from the existing `council roster`, plus a way to pass explicit Figure choices into `council ask` (flag vs. interactive picker) — parallels the profile-selection UI being designed in the companion `user-profiles` PRD, and both may want the same picker pattern.
- **Content sourcing for new Figures**: needs a decision on process for drafting each new Figure's Worldview/Biography/Known positions accurately (research process, review step) versus just generating plausible-sounding content — accuracy matters more here than for the selection-layer plumbing.

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
