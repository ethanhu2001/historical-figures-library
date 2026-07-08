import { useRef, useState } from "react";
import { askQuestion, connect, type LibraryEntry, type ServerMessage } from "./api";
import QuestionForm from "./components/QuestionForm";
import TranscriptView from "./components/TranscriptView";
import CabinetPicker from "./components/CabinetPicker";
import ClarifyingPrompt from "./components/ClarifyingPrompt";
import ResultPanel from "./components/ResultPanel";

type Phase = "idle" | "waiting" | "choosing_cabinet" | "answering_clarifying" | "done" | "error";

interface Turn {
  speaker: string;
  text: string;
}

interface Result {
  kind: "synthesis" | "direct_answer";
  text: string;
  seated: string[];
  transcript_path: string;
}

export default function App() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [cabinetLibrary, setCabinetLibrary] = useState<LibraryEntry[]>([]);
  const [cabinetError, setCabinetError] = useState<string | null>(null);
  const [clarifyingPrompt, setClarifyingPrompt] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const socketRef = useRef<ReturnType<typeof connect> | null>(null);

  function reset() {
    socketRef.current?.close();
    socketRef.current = null;
    setPhase("idle");
    setTurns([]);
    setCabinetLibrary([]);
    setCabinetError(null);
    setClarifyingPrompt(null);
    setResult(null);
    setErrorMessage(null);
  }

  function handleMessage(message: ServerMessage) {
    switch (message.type) {
      case "turn":
        setTurns((prev) => [...prev, { speaker: message.speaker, text: message.text }]);
        break;
      case "choose_cabinet":
        setCabinetError(null);
        setCabinetLibrary(message.library);
        setPhase("choosing_cabinet");
        break;
      case "cabinet_error":
        setCabinetError(message.message);
        break;
      case "clarifying_question":
        setClarifyingPrompt(message.prompt);
        setPhase("answering_clarifying");
        break;
      case "result":
        setResult(message);
        break;
      case "error":
        setErrorMessage(message.message);
        setPhase("error");
        break;
      case "done":
        setPhase((prev) => (prev === "error" ? "error" : "done"));
        socketRef.current?.close();
        break;
    }
  }

  async function handleAsk(question: string) {
    setTurns([]);
    setResult(null);
    setErrorMessage(null);
    setPhase("waiting");
    try {
      const socket = connect(handleMessage);
      socketRef.current = socket;
      await askQuestion(question);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : String(err));
      setPhase("error");
    }
  }

  function handleCabinetConfirm(names: string[]) {
    socketRef.current?.reply(names);
    setPhase("waiting");
  }

  function handleCabinetAutoSelect() {
    socketRef.current?.reply(null);
    setPhase("waiting");
  }

  function handleClarifyingAnswer(answer: string) {
    socketRef.current?.reply(answer);
    setClarifyingPrompt(null);
    setPhase("waiting");
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 bg-stone-50 p-6 dark:bg-stone-900">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-50">Council</h1>

      {phase === "idle" && <QuestionForm onSubmit={handleAsk} />}

      <TranscriptView turns={turns} />

      {phase === "choosing_cabinet" && (
        <CabinetPicker
          library={cabinetLibrary}
          error={cabinetError}
          onConfirm={handleCabinetConfirm}
          onAutoSelect={handleCabinetAutoSelect}
        />
      )}

      {phase === "answering_clarifying" && clarifyingPrompt && (
        <ClarifyingPrompt prompt={clarifyingPrompt} onSubmit={handleClarifyingAnswer} />
      )}

      {phase === "waiting" && !result && (
        <div className="text-stone-500 dark:text-stone-400">The Convener is thinking…</div>
      )}

      {result && (
        <ResultPanel
          kind={result.kind}
          text={result.text}
          seated={result.seated}
          transcriptPath={result.transcript_path}
          onReset={reset}
        />
      )}

      {phase === "error" && errorMessage && (
        <div className="flex flex-col gap-3 rounded-md border border-red-300 bg-red-50 p-4 dark:border-red-700 dark:bg-red-950">
          <div className="text-red-800 dark:text-red-200">{errorMessage}</div>
          <button
            type="button"
            onClick={reset}
            className="self-start rounded-md border border-red-400 px-4 py-2 font-medium text-red-800 dark:text-red-200"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  );
}
