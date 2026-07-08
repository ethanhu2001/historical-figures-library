from __future__ import annotations

import asyncio
import os
import queue
import threading
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from council.convener import Convener, TooFewFigures, UnknownFigure, resolve_picks
from council.figure import Figure, load_figures
from council.llm import LLMClient
from council.paths import REPO_ROOT
from council.session import Session
from council.transcript import save_transcript

FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"

app = FastAPI()

_figures = load_figures()
_lock = threading.Lock()


@dataclass
class ActiveSession:
    session: Session
    outbound: "queue.Queue[dict]" = field(default_factory=queue.Queue)
    inbound: "queue.Queue[dict]" = field(default_factory=queue.Queue)
    thread: threading.Thread | None = None


_active: ActiveSession | None = None


class AskRequest(BaseModel):
    question: str


def _run_session(active: ActiveSession, figures: list[Figure]) -> None:
    def ask_user(prompt: str) -> str:
        active.outbound.put({"type": "clarifying_question", "prompt": prompt})
        return active.inbound.get()["value"]

    def on_turn(speaker: str, text: str) -> None:
        active.outbound.put({"type": "turn", "speaker": speaker, "text": text})

    def pick_candidates() -> list[Figure] | None:
        active.outbound.put(
            {
                "type": "choose_cabinet",
                "library": [
                    {"name": f.name, "worldview": f.worldview.splitlines()[0]} for f in figures
                ],
            }
        )
        while True:
            names = active.inbound.get()["value"]
            if not names:
                return None
            try:
                return resolve_picks(names, figures)
            except (UnknownFigure, TooFewFigures) as exc:
                active.outbound.put({"type": "cabinet_error", "message": str(exc)})

    try:
        result = active.session.run(
            ask_user=ask_user, on_turn=on_turn, pick_candidates=pick_candidates
        )
        path = save_transcript(active.session)
        active.outbound.put(
            {
                "type": "result",
                "kind": "synthesis" if active.session.seated else "direct_answer",
                "text": result,
                "seated": [f.name for f in active.session.seated],
                "transcript_path": os.path.relpath(path, REPO_ROOT),
            }
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to the browser, not swallowed
        active.outbound.put({"type": "error", "message": str(exc)})
    finally:
        active.outbound.put({"type": "done"})


@app.post("/api/ask", status_code=202)
def ask(req: AskRequest) -> dict:
    global _active
    with _lock:
        if _active is not None and _active.thread is not None and _active.thread.is_alive():
            raise HTTPException(status_code=409, detail="A session is already running")
        convener = Convener(llm=LLMClient(), library=_figures)
        session = Session(question=req.question, convener=convener)
        active = ActiveSession(session=session)
        thread = threading.Thread(target=_run_session, args=(active, _figures), daemon=True)
        active.thread = thread
        _active = active
        thread.start()
    return {"status": "started"}


@app.websocket("/api/ws")
async def ws(websocket: WebSocket) -> None:
    await websocket.accept()
    active = _active
    if active is None:
        await websocket.close(code=1000)
        return

    loop = asyncio.get_event_loop()

    async def forward_outbound() -> None:
        while True:
            message = await loop.run_in_executor(None, active.outbound.get)
            await websocket.send_json(message)
            if message["type"] == "done":
                break

    async def forward_inbound() -> None:
        try:
            while True:
                data = await websocket.receive_json()
                active.inbound.put(data)
        except WebSocketDisconnect:
            pass

    inbound_task = asyncio.create_task(forward_inbound())
    try:
        await forward_outbound()
    finally:
        inbound_task.cancel()


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
