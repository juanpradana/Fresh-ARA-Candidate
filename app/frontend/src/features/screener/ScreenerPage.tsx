import { useEffect, useState } from "react";
import {
  getBacktestSummary,
  getRecentJobRuns,
  getScreener,
  getScreenerCsvExportUrl,
  type BacktestSummary,
  type JobRun,
  type ScreenerFilters,
  type ScreenerRow,
} from "../../shared/api/client";

export function ScreenerPage() {
  const [rows, setRows] = useState<ScreenerRow[]>([]);
  const [backtest, setBacktest] = useState<BacktestSummary | null>(null);
  const [latestRun, setLatestRun] = useState<JobRun | null>(null);
  const [filters, setFilters] = useState<ScreenerFilters>({
    screenDate: "2026-05-06",
    preset: "balanced",
    start: "2026-05-01",
    end: "2026-05-31",
  });

  const loadData = (nextFilters: ScreenerFilters) => {
    getScreener({ screenDate: nextFilters.screenDate, preset: nextFilters.preset }).then(setRows);
    getBacktestSummary({ start: nextFilters.start, end: nextFilters.end, preset: nextFilters.preset }).then(setBacktest);
    getRecentJobRuns(1).then((runs) => setLatestRun(runs[0] ?? null));
  };

  useEffect(() => {
    loadData(filters);
  }, []);

  return (
    <div>
      <h1>Fresh ARA Screener</h1>
      <div>
        <label htmlFor="preset">Preset</label>
        <select
          id="preset"
          value={filters.preset}
          onChange={(event) => setFilters((prev) => ({ ...prev, preset: event.target.value }))}
        >
          <option value="conservative">conservative</option>
          <option value="balanced">balanced</option>
          <option value="aggressive">aggressive</option>
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
          <p>Status: {latestRun.status}</p>
          {latestRun.error_message && <p>Error: {latestRun.error_message}</p>}
        </section>
      )}
      <ul>{rows.map((row, index) => <li key={`${row.ticker}-${index}`}>{row.ticker}</li>)}</ul>
    </div>
  );
}
