from __future__ import annotations

from council.figure import Figure
from council.session import Session
from council.web import ActiveSession, _run_session


def figure(name):
    return Figure(slug=name.lower(), name=name, worldview="w", system_prompt=f"# {name}")


def _drain(active):
    messages = []
    while not active.outbound.empty():
        messages.append(active.outbound.get_nowait())
    return messages


def _redirect_transcripts(monkeypatch, tmp_path):
    import council.web as web

    def fake_save_transcript(session, sessions_dir=None):
        from council.transcript import save_transcript

        return save_transcript(session, sessions_dir=tmp_path)

    monkeypatch.setattr(web, "save_transcript", fake_save_transcript)


class DirectAnswerConvener:
    def needs_debate(self, question):
        return False

    def answer_directly(self, question):
        return "It's sunny."


def test_trivial_question_produces_a_turn_then_a_direct_answer_result(monkeypatch, tmp_path):
    _redirect_transcripts(monkeypatch, tmp_path)
    session = Session(question="What's the weather?", convener=DirectAnswerConvener())
    active = ActiveSession(session=session)

    _run_session(active, figures=[])

    messages = _drain(active)
    assert messages[0] == {"type": "turn", "speaker": "User", "text": "What's the weather?"}
    assert messages[1]["type"] == "result"
    assert messages[1]["kind"] == "direct_answer"
    assert messages[1]["text"] == "It's sunny."
    assert messages[1]["seated"] == []
    assert messages[-1] == {"type": "done"}


class ClarifyingConvener:
    """Debates once, asks a clarifying question, then ends after the answer."""

    def __init__(self, seated):
        self.seated = seated
        self._turn = 0

    def needs_debate(self, question):
        return True

    def select_figures(self, question, candidates=None):
        return self.seated

    def choose_next_speaker(self, seated, transcript):
        self._turn += 1
        return seated[0] if self._turn <= 2 else None

    def prompt_figure(self, figure, transcript):
        from council.llm import Completion

        if self._turn == 1:
            return Completion(text="<clarifying_question>What's your budget?</clarifying_question>")
        return Completion(text="Final reply.")

    def synthesize(self, transcript):
        return "Synthesis text"


def test_clarifying_question_round_trips_through_the_inbound_queue(monkeypatch, tmp_path):
    _redirect_transcripts(monkeypatch, tmp_path)
    a = figure("A")
    session = Session(question="Q?", convener=ClarifyingConvener(seated=[a]))
    active = ActiveSession(session=session)
    active.inbound.put({"value": None})  # auto-select the Cabinet
    active.inbound.put({"value": "Modest budget"})  # answer to the clarifying question

    _run_session(active, figures=[a])

    messages = _drain(active)
    clarifying = next(m for m in messages if m["type"] == "clarifying_question")
    assert clarifying["prompt"] == "(A) What's your budget?"
    answer_turn = next(m for m in messages if m["type"] == "turn" and m["speaker"] == "User" and m["text"] == "Modest budget")
    assert answer_turn is not None
    result = messages[-2]
    assert result["type"] == "result"
    assert result["kind"] == "synthesis"
    assert result["text"] == "Synthesis text"
    assert result["seated"] == ["A"]
    assert messages[-1] == {"type": "done"}


class CabinetPickConvener:
    def __init__(self, seated_after_pick):
        self.seated_after_pick = seated_after_pick
        self.received_candidates = "not called"

    def needs_debate(self, question):
        return True

    def select_figures(self, question, candidates=None):
        self.received_candidates = candidates
        return self.seated_after_pick

    def choose_next_speaker(self, seated, transcript):
        return None

    def synthesize(self, transcript):
        return "Synthesis text"


def test_valid_cabinet_pick_is_resolved_and_forwarded_to_select_figures(monkeypatch, tmp_path):
    _redirect_transcripts(monkeypatch, tmp_path)
    a, b, c = figure("A"), figure("B"), figure("C")
    convener = CabinetPickConvener(seated_after_pick=[a, b, c])
    session = Session(question="Q?", convener=convener)
    active = ActiveSession(session=session)
    active.inbound.put({"value": ["A", "B", "C"]})

    _run_session(active, figures=[a, b, c])

    assert [f.name for f in convener.received_candidates] == ["A", "B", "C"]
    messages = _drain(active)
    choose_cabinet = next(m for m in messages if m["type"] == "choose_cabinet")
    assert {f["name"] for f in choose_cabinet["library"]} == {"A", "B", "C"}


def test_empty_cabinet_pick_means_auto_select(monkeypatch, tmp_path):
    _redirect_transcripts(monkeypatch, tmp_path)
    a, b, c = figure("A"), figure("B"), figure("C")
    convener = CabinetPickConvener(seated_after_pick=[a, b, c])
    session = Session(question="Q?", convener=convener)
    active = ActiveSession(session=session)
    active.inbound.put({"value": None})

    _run_session(active, figures=[a, b, c])

    assert convener.received_candidates is None


def test_invalid_cabinet_pick_reports_an_error_and_waits_for_another_reply(monkeypatch, tmp_path):
    _redirect_transcripts(monkeypatch, tmp_path)
    a, b, c = figure("A"), figure("B"), figure("C")
    convener = CabinetPickConvener(seated_after_pick=[a, b, c])
    session = Session(question="Q?", convener=convener)
    active = ActiveSession(session=session)
    active.inbound.put({"value": ["Someone Unknown"]})
    active.inbound.put({"value": ["A", "B", "C"]})

    _run_session(active, figures=[a, b, c])

    messages = _drain(active)
    assert any(m["type"] == "cabinet_error" for m in messages)
    assert [f.name for f in convener.received_candidates] == ["A", "B", "C"]


class BlowsUpConvener:
    def needs_debate(self, question):
        raise RuntimeError("boom")


def test_exception_in_session_run_is_reported_as_an_error(monkeypatch, tmp_path):
    _redirect_transcripts(monkeypatch, tmp_path)
    session = Session(question="Q?", convener=BlowsUpConvener())
    active = ActiveSession(session=session)

    _run_session(active, figures=[])

    messages = _drain(active)
    assert messages[-2] == {"type": "error", "message": "boom"}
    assert messages[-1] == {"type": "done"}
