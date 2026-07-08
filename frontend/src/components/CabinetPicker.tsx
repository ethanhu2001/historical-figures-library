import { useState } from "react";
import type { LibraryEntry } from "../api";

// Mirrors council.convener.MIN_FIGURES; a client-side hint only, the server
// is authoritative via resolve_picks().
const MIN_FIGURES = 3;

interface Props {
  library: LibraryEntry[];
  error: string | null;
  onConfirm: (names: string[]) => void;
  onAutoSelect: () => void;
}

export default function CabinetPicker({ library, error, onConfirm, onAutoSelect }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  function toggle(name: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  }

  return (
    <div className="flex flex-col gap-3 rounded-md border border-stone-200 p-4 dark:border-stone-700">
      <div className="font-semibold text-stone-800 dark:text-stone-100">
        Pick Figures for this Cabinet (at least {MIN_FIGURES}), or auto-select from the full
        Library.
      </div>
      {error && <div className="text-sm text-red-600 dark:text-red-400">{error}</div>}
      <ul className="flex flex-col gap-1">
        {library.map((figure) => (
          <li key={figure.name}>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selected.has(figure.name)}
                onChange={() => toggle(figure.name)}
              />
              <span className="text-stone-800 dark:text-stone-100">{figure.name}</span>
              <span className="text-sm text-stone-500 dark:text-stone-400">
                — {figure.worldview}
              </span>
            </label>
          </li>
        ))}
      </ul>
      <div className="flex gap-3">
        <button
          type="button"
          disabled={selected.size < MIN_FIGURES}
          onClick={() => onConfirm(Array.from(selected))}
          className="rounded-md bg-stone-800 px-4 py-2 font-medium text-white disabled:opacity-40 dark:bg-stone-200 dark:text-stone-900"
        >
          Confirm Cabinet
        </button>
        <button
          type="button"
          onClick={onAutoSelect}
          className="rounded-md border border-stone-300 px-4 py-2 font-medium text-stone-800 dark:border-stone-600 dark:text-stone-100"
        >
          Auto-select
        </button>
      </div>
    </div>
  );
}
