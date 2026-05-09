import type { ScreenerDetail, ScreenerHistoryRow } from "../../../shared/api/client";

type TickerDetailDrawerProps = {
  open: boolean;
  selectedTicker: string | null;
  detail: ScreenerDetail;
  history: ScreenerHistoryRow[];
  onClose: () => void;
};

export function TickerDetailDrawer({
  open,
  selectedTicker,
  detail,
  history,
  onClose,
}: TickerDetailDrawerProps) {
  if (!open) {
    return null;
  }

  const passItems = [
    ["pass_vol_ratio", detail?.pass_vol_ratio ?? 0],
    ["pass_range_pct", detail?.pass_range_pct ?? 0],
    ["pass_price_action", detail?.pass_price_action ?? 0],
    ["pass_is_ara_t0", detail?.pass_is_ara_t0 ?? 0],
  ] as const;

  return (
    <section data-testid="ticker-detail-drawer" className="rounded-lg border border-zinc-800 bg-zinc-900/70 p-3">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-medium text-zinc-200">Selected Ticker</h2>
          <p className="mt-1 font-data text-base text-zinc-100">Selected: {selectedTicker}</p>
          {detail && <p className="mt-1 text-sm text-zinc-300">Score: {typeof detail.score === "number" ? detail.score.toFixed(2) : "-"}</p>}
        </div>
        <button
          type="button"
          className="rounded border border-zinc-700 px-2 py-1 text-xs text-zinc-300 hover:border-zinc-500"
          onClick={onClose}
        >
          Close Detail
        </button>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {passItems.map(([label, value]) => (
          <p key={label} className="rounded-md border border-zinc-800 bg-zinc-950/50 px-2 py-1 text-sm text-zinc-200">
            {label}: {value}
          </p>
        ))}
      </div>

      {history.length > 0 && <p className="mt-3 text-sm text-zinc-300">History rows: {history.length}</p>}
      {history.length > 0 && (
        <ul className="mt-2 space-y-1">
          {history.map((row, index) => (
            <li key={`${row.screen_date ?? "na"}-${index}`} className="font-data text-xs text-zinc-400">
              {row.screen_date ?? "-"} {typeof row.score === "number" ? row.score.toFixed(2) : "-"}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
