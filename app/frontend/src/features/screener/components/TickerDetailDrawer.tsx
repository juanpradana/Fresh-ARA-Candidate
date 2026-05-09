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

  return (
    <section data-testid="ticker-detail-drawer" className="mt-4 rounded-lg border border-zinc-800 bg-zinc-900/70 p-3">
      <h2>Selected Ticker</h2>
      <button
        type="button"
        className="mb-2 rounded border border-zinc-700 px-2 py-1"
        onClick={onClose}
      >
        Close Detail
      </button>
      <p>Selected: {selectedTicker}</p>
      {detail && <p>Score: {typeof detail.score === "number" ? detail.score.toFixed(2) : "-"}</p>}
      <p>pass_vol_ratio: {detail?.pass_vol_ratio ?? 0}</p>
      <p>pass_range_pct: {detail?.pass_range_pct ?? 0}</p>
      <p>pass_price_action: {detail?.pass_price_action ?? 0}</p>
      <p>pass_is_ara_t0: {detail?.pass_is_ara_t0 ?? 0}</p>
      {history.length > 0 && <p>History rows: {history.length}</p>}
      {history.length > 0 && (
        <ul>
          {history.map((row, index) => (
            <li key={`${row.screen_date ?? "na"}-${index}`}>{row.screen_date ?? "-"} {typeof row.score === "number" ? row.score.toFixed(2) : "-"}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
