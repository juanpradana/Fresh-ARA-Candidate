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
    <section data-testid="screener-table-section">
      <ul>
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
              className={rowClass}
              onClick={() => onSelect(row.ticker)}
            >
              {row.ticker}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
