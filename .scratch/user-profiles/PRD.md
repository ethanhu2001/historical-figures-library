Status: needs-triage

# User Profiles: persistent user history and profile selection

## Problem Statement

Every time the user starts a new `council ask` Session, they have to re-explain
who they are — their situation, background, and relevant context — before the
Council can debate their question meaningfully. This is repetitive and painful
for a tool meant to be used often, and it means Figures often argue from an
under-informed picture of the user until context leaks out over the course of
the debate (or gets asked for via a Clarifying Question).

## Solution

Let the user save a durable profile ("backstory") that persists across
Sessions and CLI invocations, so the Council already knows who they are when
a Session starts. Support multiple profiles (e.g. different life contexts),
with a way to select which one is active, refresh/edit an existing one, or
add a new one from scratch.

## User Stories

1. As a repeat user, I want the Council to already know my backstory, so that I don't have to re-explain myself at the start of every Session.
2. As a user with more than one context I ask about (e.g. career vs. personal life), I want to save multiple profiles, so I can pick the right one for a given question.
3. As a user, I want to choose which profile is active before or when starting a Session, so Figures address the right context.
4. As a user, I want a sensible default (e.g. last-used profile, or an explicit "no profile") when I don't specify one, so I'm not forced to choose every time.
5. As a user, I want to create a new profile from scratch, so I can set up context for a new persona or scenario.
6. As a user, I want to edit/refresh an existing profile's backstory, so it stays current as my life situation changes.
7. As a user, I want to list my saved profiles, so I can see what's available and decide what to do with each.
8. As a user, I want to delete a profile I no longer need, so stale context doesn't accumulate or get accidentally selected.
9. As a first-time user with no profile yet, I want the tool to still work (e.g. by prompting me to create one, or by proceeding with no profile), so onboarding isn't blocked.
10. As a user, I want the profile's content to actually reach the Figures/Convener as context (not just be stored inertly), so the whole point of not re-explaining myself is achieved.
11. As a user, I want my profile stored locally on my machine (not sent anywhere I don't expect), consistent with how Figures and transcripts are already stored as local files.

## Implementation Decisions

Open — flagged for a design pass before this is `ready-for-agent`:

- **Storage shape**: this repo already stores per-entity content as one markdown file per entity (`figures/<slug>.md`, `sessions/<slug>.md`). A `profiles/<slug>.md` pattern would be consistent, but needs a decision on required structure (is a profile just freeform prose, or does it have sections like the Figure `TEMPLATE.md`?).
- **How profile context reaches a Session**: candidates are (a) prepend to the question text passed into `Session.run`, (b) inject as an added block in the prompt `Convener.prompt_figure` builds for each Figure, or (c) give the Convener a separate "About the user" input it can hand to Figures. This interacts with `src/council/session.py` and `src/council/convener.py` and should be resolved as a seam decision, not guessed. (Note: as of the `f3deea9` refactor, figure-prompting lives in `Convener.prompt_figure`, not `Session._figure_speak` — that method no longer exists.)
- **CLI surface**: likely new `council profile` subcommands (`list`, `create`, `edit`, `use`) alongside the existing `ask` and `roster` commands in `src/council/cli.py`, plus a way to pick a profile for a given `ask` invocation (flag vs. interactive picker).
- **"Active" profile persistence**: needs a decision on where "which profile is currently active" is stored between CLI invocations (a small state file, vs. requiring an explicit flag every time).

## Testing Decisions

- Follow existing test patterns in `tests/test_session.py` and `tests/test_figure.py` (unit tests against the module boundary, not the CLI).
- A profile-loading module should be testable the same way `load_figures()` is exercised in `tests/test_figure.py` — load-from-disk, list, and validation behavior are the natural seams.
- Session-level tests should confirm the active profile's content actually reaches the transcript/prompt context, not just that it's stored.

## Out of Scope

- Multi-user / multi-machine sync of profiles (this is a personal local tool).
- Any authentication or access control around profiles.
- Automatically inferring profile content from past Sessions/transcripts (this PRD is about explicit, user-authored backstory — not derived history).

## Further Notes

This PRD intentionally stops short of locking in the storage/injection design — those are real seam decisions (see `docs/agents/domain.md` / ADRs for how this repo likes to record such decisions) and are worth a short design or domain-modeling pass before implementation starts, since they'll also matter for the companion `figure-library-expansion` feature (a user picking figures and a user picking a profile are two similar "selection layer" problems and may want the same UI pattern).
