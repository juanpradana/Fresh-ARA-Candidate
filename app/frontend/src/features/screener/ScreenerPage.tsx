import { useEffect, useState } from "react";
import {
  getBacktestSummary,
  getRecentJobRuns,
  getScreener,
  getScreenerCsvExportUrl,
  type BacktestSummary,
  type JobRun,
  type ScreenerRow,
} from "../../shared/api/client";

export function ScreenerPage() {
  const [rows, setRows] = useState<ScreenerRow[]>([]);
  const [backtest, setBacktest] = useState<BacktestSummary | null>(null);
  const [latestRun, setLatestRun] = useState<JobRun | null>(null);

  useEffect(() => {
    getScreener().then(setRows);
    getBacktestSummary().then(setBacktest);
    getRecentJobRuns().then((runs) => setLatestRun(runs[0] ?? null));
  }, []);

  return (
    <div>
      <h1>Fresh ARA Screener</h1>
      <a href={getScreenerCsvExportUrl()}>Export CSV</a>
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
