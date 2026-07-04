Status: ready-for-agent

# Figure web search: internet-grounded factual claims

## Problem Statement

Today a Figure answers purely from its system prompt (`figures/<slug>.md`)
and the LLM's training knowledge (`Convener.prompt_figure` in
`src/council/convener.py` sends only the transcript-so-far —
see `src/council/convener.py:29-36`). For questions touching current events,
recent statistics, or any fact outside a Figure's authored `Known positions`,
a Figure has no way to check itself — it either guesses, states something
stale or wrong, or falls back to a Clarifying Question directed at the user,
even when the user doesn't know the answer either. There's currently no
mechanism for a Figure (or the Convener) to look anything up.

## Solution

Give Figures (and/or the Convener — see open question below) the ability to
search the internet mid-Session when they need factual grounding they don't
already have, analogous to how a Figure can already pause and ask the user a
Clarifying Question — except a web search resolves itself rather than
blocking on the user.

## User Stories

1. As a user, I want Figures to look up current facts (recent events, statistics, data) instead of guessing from stale training knowledge, so their arguments are grounded in reality.
2. As a user, I want it clear in the transcript when a claim came from a search versus from a Figure's Worldview/Known positions, so I can tell what's asserted vs. looked up.
3. As a user, I want Figures to search only when they genuinely need external grounding — not reflexively on every turn — so debates stay fast and don't turn into search-spam.
4. As a user, I want the Convener to still be able to challenge a search-sourced claim during the debate and address it in the Synthesis, consistent with how it already judges "which claims held up under challenge."
5. As a user, I want search results to come from the actual internet, not be invented by the model, so a "citation" is never a hallucinated one.
6. As a user, I want visibility into what was searched and what came back (even if just in a verbose/debug trace), so I can verify a Figure's sourcing if I want to.
7. As a maintainer, I want search plumbed through the existing `LLMClient` wrapper (`src/council/llm.py`) rather than Figures or the Convener calling a search API directly, preserving the "provider swap stays contained here" seam the wrapper already exists for.
8. As a user, I want a bounded number of searches per Session (or per turn), so cost and latency stay predictable — mirroring how `ROUNDS_PER_FIGURE` already bounds debate length in `src/council/session.py`.
9. As a user, I want a Session to keep working (Figure still answers, just without fresh grounding) if the search call errors or times out, so a network hiccup never hard-fails a debate.
10. As a user, I want guidance on when a Figure reaches for search versus a Clarifying Question to the user — search for facts the world knows, Clarifying Question for facts only the user knows — so the two mechanisms don't collide or get misused.

## Implementation Decisions

Locked in via grilling session on 2026-07-03 (see ADR-0003):

- **Mechanism**: Anthropic's native server-side web search tool, passed via the `tools` argument to `messages.create` — not a client-managed tool-loop against a third-party search vendor. Claude decides when to search and the API executes it server-side, returning results as content blocks in the same response; no second round-trip, no new vendor/API key. This keeps `LLMClient` a thin, single-provider wrapper, consistent with ADR-0001's single-model stance.
- **Who gets search**: Figures only, via `Convener.prompt_figure` (`src/council/convener.py`). `select_figures`, `choose_next_speaker`, and `synthesize` do not request the tool — they're orchestration and summarization of claims Figures already made, not places a new factual claim should originate.
- **Budget/limits**: enforced via the web search tool's own `max_uses` parameter, scoped to the single `messages.create` call `prompt_figure` makes per Figure turn. A new constant (e.g. `MAX_SEARCHES_PER_TURN`), analogous to `ROUNDS_PER_FIGURE` (`src/council/session.py`), sets this — no new Session-level search-tracking state required.
- **Transcript representation**: `LLMClient.complete()`'s return type changes from a bare `str` to a small result carrying `text` plus any `citations` the response's content blocks carried. Block-handling complexity (text vs. server-side search-result blocks vs. cited-text blocks) lives once inside `complete()`. The three orchestration call sites never request the tool, so their `citations` is always empty and they read `.text` same as today; only `prompt_figure` reads both. `Turn` (`src/council/session.py`) gains an optional `citations` field so `transcript.py` can render sources under a turn when present — satisfying "visible in the transcript" without new infrastructure.
- **Relationship to Clarifying Questions**: `figures/TEMPLATE.md`'s "Debate behavior" section currently says only "ask the user a direct clarifying question" when information is lacking. That sentence is updated to distinguish the two: ask the *user* for things only they would know (their situation, preferences, values); rely on search — automatic, no tag needed — for facts the world knows. This is part of this PRD's implementation, not a follow-on.

## Testing Decisions

- Tests should mock the search boundary the same way LLM calls are presumably already mocked for `tests/test_session.py` / `tests/test_convener.py` — no real network calls in the test suite.
- Cover: a Figure's turn that triggers a search and incorporates the result; the graceful-degradation path when search fails; and the per-Session/turn budget being enforced.

## Out of Scope

- General-purpose user-facing web search / browsing (this is about Figures grounding their own claims mid-debate, not a search feature for the user).
- Persistent caching or indexing of search results across Sessions.
- Fact-checking or auto-correcting a Figure's Worldview-driven opinions — search is for external facts, not for adjudicating value-laden disagreements (Synthesis already handles those by presenting both sides, per `docs/agents/domain.md`).

## Further Notes

This shares a dependency with the other open PRDs in this repo: like
`figure-library-expansion`, a larger and more historically/temporally diverse
library increases the odds a Figure needs external grounding on a topic
outside its authored `Known positions`, and like `user-profiles`, giving the
Session richer inputs (profile context, search results) argues for settling
the "how does extra context reach a Figure's prompt" seam decision once,
rather than solving it three separate times per feature.
