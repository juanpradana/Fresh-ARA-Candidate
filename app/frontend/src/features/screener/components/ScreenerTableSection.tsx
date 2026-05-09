import type { ScreenerRow } from "../../../shared/api/client";

export function ScreenerTableSection({
  rows,
  selectedTicker,
  onSelect,
}: {
  rows: ScreenerRow[];
  selectedTicker: string | null;
  onSelect: (ticker: string) => void;
}) {
  return (
    <section data-testid="screener-table-section" className="hidden rounded-lg border border-zinc-800 bg-zinc-900/40 p-2 md:block">
      <ul className="space-y-1">
        {rows.map((row, index) => {
          const isSelected = selectedTicker === row.ticker;
          const hasSelection = selectedTicker !== null;
          const rowClass = isSelected
            ? "font-data border border-emerald-400 shadow-row-glow"
            : hasSelection
              ? "font-data opacity-60"
              : "font-data";

          return (
            <li
              key={`${row.ticker}-${index}`}
              data-testid={`screener-row-${row.ticker}`}
              className={`${rowClass} cursor-pointer rounded-md border-zinc-800 bg-zinc-950/40 px-3 py-2 text-sm transition hover:bg-zinc-900/80`}
              onClick={() => onSelect(row.ticker)}
            >
              <div className="flex items-center justify-between gap-3">
                <span>{row.ticker}</span>
                <span className="text-xs text-zinc-400">#{typeof row.rank_num === "number" ? row.rank_num : "-"}</span>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
