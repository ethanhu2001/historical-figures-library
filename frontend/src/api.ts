export interface LibraryEntry {
  name: string;
  worldview: string;
}

export type ServerMessage =
  | { type: "turn"; speaker: string; text: string }
  | { type: "choose_cabinet"; library: LibraryEntry[] }
  | { type: "cabinet_error"; message: string }
  | { type: "clarifying_question"; prompt: string }
  | {
      type: "result";
      kind: "synthesis" | "direct_answer";
      text: string;
      seated: string[];
      transcript_path: string;
    }
  | { type: "error"; message: string }
  | { type: "done" };

export async function askQuestion(question: string): Promise<void> {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed with status ${response.status}`);
  }
}

export function connect(onMessage: (message: ServerMessage) => void): {
  reply: (value: unknown) => void;
  close: () => void;
} {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const socket = new WebSocket(`${protocol}//${window.location.host}/api/ws`);

  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data) as ServerMessage);
  };

  return {
    reply: (value: unknown) => socket.send(JSON.stringify({ type: "reply", value })),
    close: () => socket.close(),
  };
}
