import type { ScreenerRow } from "../../../shared/api/client";

export function ScreenerCardListSection({
  rows,
  selectedTicker,
  onSelect,
}: {
  rows: ScreenerRow[];
  selectedTicker: string | null;
  onSelect: (ticker: string) => void;
}) {
  return (
    <section data-testid="screener-card-section" className="grid gap-2 md:hidden">
      {rows.map((row, index) => {
        const isSelected = selectedTicker === row.ticker;

        return (
          <article
            key={`${row.ticker}-card-${index}`}
            className={`font-data rounded-md border px-3 py-2 ${isSelected ? "border-emerald-400 shadow-row-glow bg-zinc-900/70" : "border-zinc-800 bg-zinc-900/50"}`}
            onClick={() => onSelect(row.ticker)}
          >
            <div className="flex items-center justify-between gap-3">
              <span>{row.ticker}</span>
              <span className="text-xs text-zinc-400">#{typeof row.rank_num === "number" ? row.rank_num : "-"}</span>
            </div>
            <div className="mt-1 grid grid-cols-3 gap-2 text-xs text-zinc-300">
              <span>Score: {typeof row.score === "number" ? row.score.toFixed(2) : "-"}</span>
              <span>Pass: {typeof row.pass_count === "number" ? row.pass_count : "-"}</span>
              <span className="text-right">{typeof row.category === "string" ? row.category : "-"}</span>
            </div>
          </article>
        );
      })}
    </section>
  );
}
