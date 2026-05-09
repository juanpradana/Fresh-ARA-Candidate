import { useEffect, useState } from "react";
import {
  getBacktestSummary,
  getDataFreshness,
  getLatestScreenDate,
  getPresets,
  getRecentJobRuns,
  getScreener,
  getScreenerCsvExportUrl,
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

export function ScreenerPage() {
  const [rows, setRows] = useState<ScreenerRow[]>([]);
  const [backtest, setBacktest] = useState<BacktestSummary | null>(null);
  const [latestRun, setLatestRun] = useState<JobRun | null>(null);
  const [presets, setPresets] = useState<PresetMeta[]>([]);
  const [freshnessWarning, setFreshnessWarning] = useState<string | null>(null);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<ScreenerDetail>(null);
  const [selectedHistory, setSelectedHistory] = useState<ScreenerHistoryRow[]>([]);
  const [filters, setFilters] = useState<ScreenerFilters>({
    screenDate: "",
    preset: "",
    start: "2026-05-01",
    end: "2026-05-31",
  });

  const loadData = (nextFilters: ScreenerFilters) => {
    getScreener({ screenDate: nextFilters.screenDate, preset: nextFilters.preset }).then((result) => {
      setRows(Array.isArray(result) ? result : []);
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
      <h1 className="font-ui">Fresh ARA Screener</h1>
      <section>
        <h2>Data Freshness</h2>
        <p>Latest screen date: {filters.screenDate}</p>
        {freshnessWarning && <p>Warning: {freshnessWarning}</p>}
      </section>
      <section>
        <h2>Disclaimer</h2>
        <p>Sinyal bersifat probabilistik, bukan jaminan hasil.</p>
      </section>
      <div>
        <label htmlFor="preset">Preset</label>
        <select
          id="preset"
          value={filters.preset}
          onChange={(event) => setFilters((prev) => ({ ...prev, preset: event.target.value }))}
        >
          {presets.map((preset) => (
            <option key={preset.preset_name} value={preset.preset_name}>{preset.preset_name}</option>
          ))}
        </select>

        <label htmlFor="screen-date">Screen Date</label>
        <input
          id="screen-date"
          value={filters.screenDate}
          onChange={(event) => setFilters((prev) => ({ ...prev, screenDate: event.target.value }))}
        />

        <label htmlFor="start-date">Backtest Start</label>
        <input
          id="start-date"
          value={filters.start}
          onChange={(event) => setFilters((prev) => ({ ...prev, start: event.target.value }))}
        />

        <label htmlFor="end-date">Backtest End</label>
        <input
          id="end-date"
          value={filters.end}
          onChange={(event) => setFilters((prev) => ({ ...prev, end: event.target.value }))}
        />

        <button onClick={() => loadData(filters)}>Apply Filters</button>
      </div>
      <a href={getScreenerCsvExportUrl({ screenDate: filters.screenDate, preset: filters.preset })}>Export CSV</a>
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
      <ul>
        {rows.map((row, index) => (
          <li
            key={`${row.ticker}-${index}`}
            data-testid={`screener-row-${row.ticker}`}
            className="font-data"
            onClick={() => setSelectedTicker(row.ticker)}
          >
            {row.ticker}
          </li>
        ))}
      </ul>
      {selectedTicker && (
        <section>
          <h2>Selected Ticker</h2>
          <p>{selectedTicker}</p>
          {selectedDetail && <p>Detail score: {selectedDetail.score ?? "-"}</p>}
          {selectedHistory.length > 0 && <p>History rows: {selectedHistory.length}</p>}
        </section>
      )}
    </div>
  );
}
