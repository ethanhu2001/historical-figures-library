# Historical Figures Library

A system where historical figures are AI agents, each defined by its own `.md` system prompt, who convene to debate questions the user brings to them.

## Language

**Library**:
The full pool of every Figure available in the system. Each Figure must meet the `TEMPLATE.md` quality bar (a distinct, well-documented Worldview), but Library membership is not hand-picked for fame, balance, or topic coverage the way a Cabinet is — it's everything available to draw from, spanning many eras and schools of thought.
_Avoid_: Council (retired — see ADR pending for figure-library-expansion), roster, catalog

**Cabinet**:
The specific Figures seated for one Session — at least 3, drawn from the Library either by the Convener's automatic relevance judgment or by the user's manual pick. The Library is everything available; the Cabinet is who actually shows up to debate a given question.
_Avoid_: Council (retired), panel, board, roster

**Figure**:
An AI agent representing a specific historical person, defined by its own `.md` system prompt that articulates their Worldview.
_Avoid_: Persona, character, agent (too generic — use Figure when referring to a historical-person agent specifically)

**Worldview**:
The distinct, coherent personal philosophy a Figure embodies (e.g. Stoicism, pragmatic authoritarianism, value investing) — the basis on which the Library is curated and on which the Convener judges a Figure's relevance when assembling a Cabinet.
_Avoid_: Philosophy (too broad — Worldview is the canonical term for a Figure's specific lens), personality, background

**Convener**:
A moderator agent, distinct from any Figure, that orchestrates a Session — selects at least 3 Figures from the Library whose Worldview is relevant to the question to form a Cabinet before the debate starts, decides speaking order, prompts Figures to respond to one another, and decides when the debate has run its course.
_Avoid_: Moderator, host (Convener is the canonical term)

**Session**:
A single instance of a Cabinet, drawn from the Library, convening to debate one question, from the user's prompt through the Convener ending the debate. Figures are expected to be maximally persuasive within their Worldview, and to rigorously challenge each other's factual and logical claims — but a Session does not force convergence on genuinely value-laden questions. A Session can pause at any point for a Clarifying Question and resume once the user answers.
_Avoid_: Debate, conversation, thread

**Clarifying Question**:
A question any Figure may pose directly to the user, mid-Session, when it needs information it doesn't have to make its case. Pauses the Session until the user answers.
_Avoid_: Follow-up, prompt

**Synthesis**:
The Convener's closing summary of a Session. For factual or logical disputes, states which claims held up under challenge. For value-laden questions with no single correct answer, presents the strongest surviving version of each Figure's position rather than forcing a winner.
_Avoid_: Summary, conclusion, verdict
