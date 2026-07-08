interface Turn {
  speaker: string;
  text: string;
}

interface Props {
  turns: Turn[];
}

export default function TranscriptView({ turns }: Props) {
  if (turns.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-4">
      {turns.map((turn, index) => (
        <div key={index} className="rounded-md border border-stone-200 p-3 dark:border-stone-700">
          <div className="mb-1 font-semibold text-stone-800 dark:text-stone-100">{turn.speaker}</div>
          <div className="whitespace-pre-wrap text-stone-700 dark:text-stone-300">{turn.text}</div>
        </div>
      ))}
    </div>
  );
}
