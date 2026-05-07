import { useEffect, useState } from "react";
import {
  getBacktestSummary,
  getScreener,
  getScreenerCsvExportUrl,
  type BacktestSummary,
  type ScreenerRow,
} from "../../shared/api/client";

export function ScreenerPage() {
  const [rows, setRows] = useState<ScreenerRow[]>([]);
  const [backtest, setBacktest] = useState<BacktestSummary | null>(null);

  useEffect(() => {
    getScreener().then(setRows);
    getBacktestSummary().then(setBacktest);
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
      <ul>{rows.map((row, index) => <li key={`${row.ticker}-${index}`}>{row.ticker}</li>)}</ul>
    </div>
  );
}
