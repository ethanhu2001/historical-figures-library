interface Props {
  kind: "synthesis" | "direct_answer";
  text: string;
  seated: string[];
  transcriptPath: string;
  onReset: () => void;
}

export default function ResultPanel({ kind, text, seated, transcriptPath, onReset }: Props) {
  return (
    <div className="flex flex-col gap-3 rounded-md border-2 border-stone-800 p-4 dark:border-stone-200">
      <div className="font-semibold text-stone-800 dark:text-stone-100">
        {kind === "synthesis" ? "Synthesis" : "Answer"}
      </div>
      {seated.length > 0 && (
        <div className="text-sm text-stone-500 dark:text-stone-400">Cabinet: {seated.join(", ")}</div>
      )}
      <div className="whitespace-pre-wrap text-stone-700 dark:text-stone-300">{text}</div>
      <div className="text-sm text-stone-500 dark:text-stone-400">
        Transcript saved to {transcriptPath}
      </div>
      <button
        type="button"
        onClick={onReset}
        className="self-start rounded-md border border-stone-300 px-4 py-2 font-medium text-stone-800 dark:border-stone-600 dark:text-stone-100"
      >
        Ask another question
      </button>
    </div>
  );
}
