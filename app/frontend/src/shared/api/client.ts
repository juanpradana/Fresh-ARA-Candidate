export type ScreenerRow = { ticker: string };

export type BacktestSummary = {
  win_rate: number;
  avg_score: number;
  total: number;
};

export type JobRun = {
  run_date: string;
  status: string;
  error_message: string | null;
};

export async function getScreener(): Promise<ScreenerRow[]> {
  const res = await fetch("/api/v1/screener");
  const json = await res.json();
  return json.data;
}

export async function getBacktestSummary(): Promise<BacktestSummary> {
  const res = await fetch("/api/v1/analytics/backtest?start=2026-05-01&end=2026-05-31&preset=balanced");
  const json = await res.json();
  return json.data;
}

export function getScreenerCsvExportUrl(): string {
  return "/api/v1/export/screener.csv?preset=balanced";
}

export async function getRecentJobRuns(): Promise<JobRun[]> {
  const res = await fetch("/api/v1/meta/job-runs?limit=1");
  const json = await res.json();
  return json.data;
}
