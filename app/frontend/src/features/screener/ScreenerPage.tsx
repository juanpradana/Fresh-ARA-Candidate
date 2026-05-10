import { useEffect, useState } from "react";
import {
  addWatchlistTicker,
  getBacktestSummary,
  getDataFreshness,
  getKpiSummary,
  getLatestScreenDate,
  getPresets,
  getRecentAlerts,
  getRecentJobRuns,
  getScreenDateRange,
  getScreener,
  getScreenerCsvExportUrl,
  getScreenerXlsxExportUrl,
  getScreenerDetail,
  getScreenerHistory,
  getWatchlistTickers,
  removeWatchlistTicker,
  type AlertEventRow,
  type BacktestSummary,
  type JobRun,
  type KpiSummary,
  type PresetMeta,
  type ScreenerDetail,
  type ScreenerFilters,
  type ScreenerHistoryRow,
  type ScreenerRow,
  type WatchlistTickerRow,
} from "../../shared/api/client";
import { ScreenerTopBar } from "./components/ScreenerTopBar";
import { SummaryStrip } from "./components/SummaryStrip";
import { ScreenerTableSection } from "./components/ScreenerTableSection";
import { ScreenerCardListSection } from "./components/ScreenerCardListSection";
import { ActionRail } from "./components/ActionRail";
import { GlobalNoticeBar } from "./components/GlobalNoticeBar";
import { TickerDetailDrawer } from "./components/TickerDetailDrawer";

export function ScreenerPage() {
  const [rows, setRows] = useState<ScreenerRow[]>([]);
  const [backtest, setBacktest] = useState<BacktestSummary | null>(null);
  const [latestRun, setLatestRun] = useState<JobRun | null>(null);
  const [presets, setPresets] = useState<PresetMeta[]>([]);
  const [freshnessWarning, setFreshnessWarning] = useState<string | null>(null);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<ScreenerDetail>(null);
  const [selectedHistory, setSelectedHistory] = useState<ScreenerHistoryRow[]>([]);
  const [watchlistRows, setWatchlistRows] = useState<WatchlistTickerRow[]>([]);
  const [alerts, setAlerts] = useState<AlertEventRow[]>([]);
  const [kpi, setKpi] = useState<KpiSummary | null>(null);
  const [isLoadingRows, setIsLoadingRows] = useState(true);
  const [filters, setFilters] = useState<ScreenerFilters>({
    screenDate: "",
    preset: "",
    start: "2026-05-01",
    end: "2026-05-31",
  });

  const loadData = (nextFilters: ScreenerFilters) => {
    setIsLoadingRows(true);
    getScreener({ screenDate: nextFilters.screenDate, preset: nextFilters.preset }).then((result) => {
      setRows(Array.isArray(result) ? result : []);
      setIsLoadingRows(false);
    });
    getBacktestSummary({ start: nextFilters.start, end: nextFilters.end, preset: nextFilters.preset }).then((result) => {
      setBacktest(result);
    });
    getRecentJobRuns(1).then((runs) => {
      setLatestRun(Array.isArray(runs) ? (runs[0] ?? null) : null);
    });
    getWatchlistTickers("default").then((result) => {
      setWatchlistRows(Array.isArray(result) ? result : []);
    });
    getRecentAlerts(5).then((result) => {
      setAlerts(Array.isArray(result) ? result : []);
    });
    getKpiSummary(nextFilters.start, nextFilters.end, nextFilters.preset).then((result) => {
      setKpi(result);
    });
  };

  useEffect(() => {
    Promise.all([getLatestScreenDate(), getPresets(), getDataFreshness(), getScreenDateRange()]).then(([latestDate, presetRows, freshness, range]) => {
      const defaultPreset = presetRows.find((item) => item.preset_name === "balanced")?.preset_name
        ?? presetRows[0]?.preset_name
        ?? "balanced";
      const defaultDate = latestDate ?? "2026-05-06";
      const defaultStart = range.min_screen_date ?? defaultDate;
      const defaultEnd = range.max_screen_date ?? defaultDate;
      const nextFilters = {
        screenDate: defaultDate,
        preset: defaultPreset,
        start: defaultStart,
        end: defaultEnd,
      };
      setPresets(presetRows);
      setFilters(nextFilters);
      setFreshnessWarning(freshness.warning);
      loadData(nextFilters);
    });
  }, []);

  useEffect(() => {
    if (!selectedTicker) {
      setSelectedDetail(null);
      setSelectedHistory([]);
      return;
    }

    getScreenerDetail({
      ticker: selectedTicker,
      screenDate: filters.screenDate,
      preset: filters.preset,
    }).then((detail) => {
      setSelectedDetail(detail);
    });

    getScreenerHistory({
      ticker: selectedTicker,
      start: filters.start,
      end: filters.end,
      preset: filters.preset,
    }).then((history) => {
      setSelectedHistory(history);
    });
  }, [selectedTicker, filters.screenDate, filters.preset, filters.start, filters.end]);

  return (
    <div data-testid="screener-shell" className="min-h-screen bg-zinc-950 text-zinc-100">
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-5 md:px-6 lg:gap-5 lg:py-6">
        <ScreenerTopBar />
        <GlobalNoticeBar screenDate={filters.screenDate} warning={freshnessWarning} />
        <ActionRail
          presets={presets}
          filters={filters}
          onChangeFilters={setFilters}
          onApply={() => loadData(filters)}
          csvExportUrl={getScreenerCsvExportUrl({ screenDate: filters.screenDate, preset: filters.preset })}
          xlsxExportUrl={getScreenerXlsxExportUrl({ screenDate: filters.screenDate, preset: filters.preset })}
        />
        <div className="grid gap-3 lg:grid-cols-2">
          {backtest && (
            <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
              <h2 className="text-sm font-medium text-zinc-200">Backtest Summary</h2>
              <div className="mt-2 space-y-1 text-sm text-zinc-300">
                <p>Win rate: {(backtest.win_rate * 100).toFixed(2)}%</p>
                <p>Average score: {backtest.avg_score.toFixed(2)}</p>
                <p>Total samples: {backtest.total}</p>
              </div>
            </section>
          )}
          {latestRun && (
            <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
              <h2 className="text-sm font-medium text-zinc-200">Daily Job Status</h2>
              <div className="mt-2 space-y-1 text-sm text-zinc-300">
                <p>Date: {latestRun.run_date}</p>
                <p>Status: {latestRun.status === "skipped" ? "skipped (non-trading day)" : latestRun.status}</p>
                {latestRun.error_message && <p>Error: {latestRun.error_message}</p>}
              </div>
            </section>
          )}
        </div>
        <SummaryStrip
          totalCandidates={rows.length}
          idealCount={rows.filter((row) => row.category === "ideal").length}
        />
        <div className="grid gap-3 lg:grid-cols-3">
          <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
            <h2 className="text-sm font-medium text-zinc-200">Watchlist (default)</h2>
            {watchlistRows.length === 0 ? (
              <p className="mt-2 text-sm text-zinc-400">No watchlist tickers.</p>
            ) : (
              <ul className="mt-2 space-y-1 text-sm text-zinc-300">
                {watchlistRows.map((row) => (
                  <li key={`${row.watchlist_name}-${row.ticker}`} className="flex items-center justify-between gap-2">
                    <span>{row.ticker}</span>
                    <button
                      className="rounded border border-zinc-700 px-2 py-0.5 text-xs text-zinc-300"
                      onClick={() => {
                        removeWatchlistTicker(row.ticker, "default").then((ok) => {
                          if (ok) {
                            getWatchlistTickers("default").then((result) => setWatchlistRows(Array.isArray(result) ? result : []));
                          }
                        });
                      }}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {selectedTicker && (
              <button
                className="mt-2 rounded border border-emerald-400 px-2 py-1 text-xs text-emerald-300"
                onClick={() => {
                  addWatchlistTicker(selectedTicker, "default").then((ok) => {
                    if (ok) {
                      getWatchlistTickers("default").then((result) => setWatchlistRows(Array.isArray(result) ? result : []));
                    }
                  });
                }}
              >
                Add selected ({selectedTicker})
              </button>
            )}
          </section>
          <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
            <h2 className="text-sm font-medium text-zinc-200">Recent Alerts</h2>
            {alerts.length === 0 ? (
              <p className="mt-2 text-sm text-zinc-400">No alerts yet.</p>
            ) : (
              <ul className="mt-2 space-y-1 text-sm text-zinc-300">
                {alerts.map((row, index) => (
                  <li key={`${row.ticker}-${row.run_date}-${index}`}>
                    {row.ticker} · {row.run_date}
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
            <h2 className="text-sm font-medium text-zinc-200">KPI Baseline</h2>
            <div className="mt-2 space-y-1 text-sm text-zinc-300">
              <p>Days: {kpi?.total_days ?? 0}</p>
              <p>Avg Precision@TopN: {(kpi?.avg_precision_at_top_n ?? 0).toFixed(2)}</p>
              <p>Screener Views: {kpi?.total_screener_views ?? 0}</p>
              <p>Alerts Views: {kpi?.total_alerts_views ?? 0}</p>
              <p>Watchlist Views: {kpi?.total_watchlist_views ?? 0}</p>
            </div>
          </section>
        </div>
        {isLoadingRows && <p className="text-sm text-zinc-400">Loading screener...</p>}
        <ScreenerTableSection
          rows={rows}
          selectedTicker={selectedTicker}
          onSelect={setSelectedTicker}
        />
        <ScreenerCardListSection rows={rows} selectedTicker={selectedTicker} onSelect={setSelectedTicker} />
        {selectedTicker && (
          <section data-testid="inline-detail-panel" className="rounded-lg border border-zinc-800 bg-zinc-900/70 p-3">
            <TickerDetailDrawer
              open={selectedTicker !== null}
              selectedTicker={selectedTicker}
              detail={selectedDetail}
              history={selectedHistory}
              onClose={() => {
                setSelectedTicker(null);
                setSelectedDetail(null);
                setSelectedHistory([]);
              }}
            />
          </section>
        )}
      </main>
    </div>
  );
}
