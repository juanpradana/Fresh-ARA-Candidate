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

export type ScreenerFilters = {
  screenDate: string;
  preset: string;
  start: string;
  end: string;
};

export async function getScreener(filters: Pick<ScreenerFilters, "screenDate" | "preset">): Promise<ScreenerRow[]> {
  const params = new URLSearchParams({
    screen_date: filters.screenDate,
    preset: filters.preset,
  });
  const res = await fetch(`/api/v1/screener?${params.toString()}`);
  const json = await res.json();
  return json.data;
}

export async function getBacktestSummary(filters: Pick<ScreenerFilters, "start" | "end" | "preset">): Promise<BacktestSummary> {
  const params = new URLSearchParams({
    start: filters.start,
    end: filters.end,
    preset: filters.preset,
  });
  const res = await fetch(`/api/v1/analytics/backtest?${params.toString()}`);
  const json = await res.json();
  return json.data;
}

export function getScreenerCsvExportUrl(filters: Pick<ScreenerFilters, "screenDate" | "preset">): string {
  const params = new URLSearchParams({
    screen_date: filters.screenDate,
    preset: filters.preset,
  });
  return `/api/v1/export/screener.csv?${params.toString()}`;
}

export async function getRecentJobRuns(limit = 1): Promise<JobRun[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  const res = await fetch(`/api/v1/meta/job-runs?${params.toString()}`);
  const json = await res.json();
  return json.data;
}
