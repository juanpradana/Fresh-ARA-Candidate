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

export type PresetMeta = {
  preset_name: string;
};

export type DataFreshnessMeta = {
  latest_screen_date: string | null;
  is_complete: boolean;
  warning: string | null;
};

export async function getScreener(filters: Pick<ScreenerFilters, "screenDate" | "preset">): Promise<ScreenerRow[]> {
  try {
    const params = new URLSearchParams({
      screen_date: filters.screenDate,
      preset: filters.preset,
    });
    const res = await fetch(`/api/v1/screener?${params.toString()}`);
    const json = await res.json();
    return Array.isArray(json?.data) ? json.data : [];
  } catch {
    return [];
  }
}

export async function getBacktestSummary(filters: Pick<ScreenerFilters, "start" | "end" | "preset">): Promise<BacktestSummary | null> {
  try {
    const params = new URLSearchParams({
      start: filters.start,
      end: filters.end,
      preset: filters.preset,
    });
    const res = await fetch(`/api/v1/analytics/backtest?${params.toString()}`);
    if (typeof res.ok === "boolean" && !res.ok) {
      return null;
    }
    const json = await res.json();
    const data = json?.data;
    if (data && typeof data.win_rate === "number" && typeof data.avg_score === "number" && typeof data.total === "number") {
      return data;
    }
    return null;
  } catch {
    return null;
  }
}

export function getScreenerCsvExportUrl(filters: Pick<ScreenerFilters, "screenDate" | "preset">): string {
  const params = new URLSearchParams({
    screen_date: filters.screenDate,
    preset: filters.preset,
  });
  return `/api/v1/export/screener.csv?${params.toString()}`;
}

export async function getRecentJobRuns(limit = 1): Promise<JobRun[]> {
  try {
    const params = new URLSearchParams({ limit: String(limit) });
    const res = await fetch(`/api/v1/meta/job-runs?${params.toString()}`);
    const json = await res.json();
    return Array.isArray(json?.data) ? json.data : [];
  } catch {
    return [];
  }
}

export async function getLatestScreenDate(): Promise<string | null> {
  try {
    const res = await fetch("/api/v1/meta/latest-screen-date");
    const json = await res.json();
    const latest = json?.data?.latest_screen_date;
    return typeof latest === "string" ? latest : null;
  } catch {
    return null;
  }
}

export async function getDataFreshness(): Promise<DataFreshnessMeta> {
  try {
    const res = await fetch("/api/v1/meta/data-freshness");
    const json = await res.json();
    const data = json?.data;
    const latest = typeof data?.latest_screen_date === "string" ? data.latest_screen_date : null;
    const isComplete = data?.is_complete === true;
    const warning = typeof data?.warning === "string"
      ? data.warning
      : (isComplete ? null : "Data EOD belum complete");
    return {
      latest_screen_date: latest,
      is_complete: isComplete,
      warning,
    };
  } catch {
    return {
      latest_screen_date: null,
      is_complete: false,
      warning: "Data EOD belum complete",
    };
  }
}

export async function getPresets(): Promise<PresetMeta[]> {
  try {
    const res = await fetch("/api/v1/meta/presets");
    const json = await res.json();
    return Array.isArray(json?.data) ? json.data : [];
  } catch {
    return [];
  }
}
