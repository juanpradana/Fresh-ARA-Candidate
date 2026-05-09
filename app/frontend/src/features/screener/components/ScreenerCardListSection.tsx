import type { ScreenerRow } from "../../../shared/api/client";

export function ScreenerCardListSection({ rows }: { rows: ScreenerRow[] }) {
  return (
    <section data-testid="screener-card-section" className="grid gap-2 md:hidden">
      {rows.map((row, index) => (
        <article key={`${row.ticker}-card-${index}`} className="font-data rounded-md border border-zinc-800 bg-zinc-900/50 px-3 py-2">
          <div className="flex items-center justify-between gap-3">
            <span>{row.ticker}</span>
            <span className="text-xs text-zinc-400">#{typeof row.rank_num === "number" ? row.rank_num : "-"}</span>
          </div>
        </article>
      ))}
    </section>
  );
}
