import { useState, type FormEvent } from "react";

interface Props {
  onSubmit: (question: string) => void;
}

export default function QuestionForm({ onSubmit }: Props) {
  const [question, setQuestion] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <label htmlFor="question" className="text-lg font-semibold text-stone-800 dark:text-stone-100">
        Bring a question to the Cabinet
      </label>
      <textarea
        id="question"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        rows={3}
        placeholder="Should I take this job?"
        className="rounded-md border border-stone-300 bg-white p-3 text-stone-900 focus:border-stone-500 focus:outline-none dark:border-stone-600 dark:bg-stone-800 dark:text-stone-100"
      />
      <button
        type="submit"
        disabled={!question.trim()}
        className="self-start rounded-md bg-stone-800 px-4 py-2 font-medium text-white disabled:opacity-40 dark:bg-stone-200 dark:text-stone-900"
      >
        Convene
      </button>
    </form>
  );
}
