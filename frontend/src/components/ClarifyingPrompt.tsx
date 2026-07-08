import { useState, type FormEvent } from "react";

interface Props {
  prompt: string;
  onSubmit: (answer: string) => void;
}

export default function ClarifyingPrompt({ prompt, onSubmit }: Props) {
  const [answer, setAnswer] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = answer.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-md border border-amber-300 bg-amber-50 p-4 dark:border-amber-700 dark:bg-amber-950"
    >
      <div className="font-semibold text-amber-900 dark:text-amber-100">[Clarifying question] {prompt}</div>
      <input
        type="text"
        value={answer}
        onChange={(event) => setAnswer(event.target.value)}
        autoFocus
        className="rounded-md border border-amber-300 bg-white p-2 text-stone-900 focus:border-amber-500 focus:outline-none dark:border-amber-700 dark:bg-stone-800 dark:text-stone-100"
      />
      <button
        type="submit"
        disabled={!answer.trim()}
        className="self-start rounded-md bg-amber-700 px-4 py-2 font-medium text-white disabled:opacity-40"
      >
        Answer
      </button>
    </form>
  );
}
