# Historical Figures Library

A system where historical figures are AI agents, each defined by its own `.md` system prompt, who convene to debate questions the user brings to them.

## Language

**Council**:
The full assembly of Figure agents available to participate in debates. Membership is curated: each Figure is chosen for having a distinct, well-documented Worldview, not for fame or domain expertise alone.
_Avoid_: Panel, board

**Figure**:
An AI agent representing a specific historical person, defined by its own `.md` system prompt that articulates their Worldview.
_Avoid_: Persona, character, agent (too generic — use Figure when referring to a historical-person agent specifically)

**Worldview**:
The distinct, coherent personal philosophy a Figure embodies (e.g. Stoicism, pragmatic authoritarianism, value investing) — the basis on which the Council is curated and on which the Convener judges a Figure's relevance to a question.
_Avoid_: Philosophy (too broad — Worldview is the canonical term for a Figure's specific lens), personality, background

**Convener**:
A moderator agent, distinct from any Figure, that orchestrates a Session — selects at least 3 Council members whose Worldview is relevant to the question before the debate starts, decides speaking order, prompts Figures to respond to one another, and decides when the debate has run its course.
_Avoid_: Moderator, host (Convener is the canonical term)

**Session**:
A single instance of the Council convening to debate one question, from the user's prompt through the Convener ending the debate. Figures are expected to be maximally persuasive within their Worldview, and to rigorously challenge each other's factual and logical claims — but a Session does not force convergence on genuinely value-laden questions. A Session can pause at any point for a Clarifying Question and resume once the user answers.
_Avoid_: Debate, conversation, thread

**Clarifying Question**:
A question any Figure may pose directly to the user, mid-Session, when it needs information it doesn't have to make its case. Pauses the Session until the user answers.
_Avoid_: Follow-up, prompt

**Synthesis**:
The Convener's closing summary of a Session. For factual or logical disputes, states which claims held up under challenge. For value-laden questions with no single correct answer, presents the strongest surviving version of each Figure's position rather than forcing a winner.
_Avoid_: Summary, conclusion, verdict
