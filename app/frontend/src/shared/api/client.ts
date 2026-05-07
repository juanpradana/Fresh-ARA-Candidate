export type ScreenerRow = { ticker: string };

export type BacktestSummary = {
  win_rate: number;
  avg_score: number;
  total: number;
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
