import type { ScreenerRow } from "../../../shared/api/client";

export function ScreenerCardListSection({ rows }: { rows: ScreenerRow[] }) {
  return (
    <section data-testid="screener-card-section" className="hidden">
      {rows.map((row, index) => (
        <article key={`${row.ticker}-card-${index}`} className="font-data">
          {row.ticker}
        </article>
      ))}
    </section>
  );
}
