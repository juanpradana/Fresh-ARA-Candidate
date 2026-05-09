import { useEffect, useState } from "react";
import {
  getBacktestSummary,
  getDataFreshness,
  getLatestScreenDate,
  getPresets,
  getRecentJobRuns,
  getScreener,
  getScreenerCsvExportUrl,
  getScreenerXlsxExportUrl,
  getScreenerDetail,
  getScreenerHistory,
  type BacktestSummary,
  type JobRun,
  type PresetMeta,
  type ScreenerDetail,
  type ScreenerFilters,
  type ScreenerHistoryRow,
  type ScreenerRow,
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
  };

  useEffect(() => {
    Promise.all([getLatestScreenDate(), getPresets(), getDataFreshness()]).then(([latestDate, presetRows, freshness]) => {
      const defaultPreset = presetRows.find((item) => item.preset_name === "balanced")?.preset_name
        ?? presetRows[0]?.preset_name
        ?? "balanced";
      const defaultDate = latestDate ?? "2026-05-06";
      const nextFilters = {
        screenDate: defaultDate,
        preset: defaultPreset,
        start: "2026-05-01",
        end: "2026-05-31",
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
      {backtest && (
        <section>
          <h2>Backtest Summary</h2>
          <p>Win rate: {(backtest.win_rate * 100).toFixed(2)}%</p>
          <p>Average score: {backtest.avg_score.toFixed(2)}</p>
          <p>Total samples: {backtest.total}</p>
        </section>
      )}
      {latestRun && (
        <section>
          <h2>Daily Job Status</h2>
          <p>Date: {latestRun.run_date}</p>
          <p>Status: {latestRun.status === "skipped" ? "skipped (non-trading day)" : latestRun.status}</p>
          {latestRun.error_message && <p>Error: {latestRun.error_message}</p>}
        </section>
      )}
      <SummaryStrip
        totalCandidates={rows.length}
        idealCount={rows.filter((row) => row.category === "ideal").length}
      />
      {isLoadingRows && <p>Loading screener...</p>}
      <ScreenerTableSection
        rows={rows}
        selectedTicker={selectedTicker}
        onSelect={setSelectedTicker}
      />
      <ScreenerCardListSection rows={rows} />
      {selectedTicker && (
        <section data-testid="inline-detail-panel" className="mt-4 rounded-lg border border-zinc-800 bg-zinc-900/70 p-3">
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
    </div>
  );
}
