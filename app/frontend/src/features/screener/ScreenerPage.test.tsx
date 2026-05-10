import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, test, vi } from "vitest";
import { ScreenerPage } from "./ScreenerPage";

beforeEach(() => {
  vi.restoreAllMocks();
});

function mockApiResponses() {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({
          data: { win_rate: 0.5, avg_score: 0.81, total: 2 },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({
          data: [
            { preset_name: "conservative" },
            { preset_name: "balanced" },
            { preset_name: "aggressive" },
          ],
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-07",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({
          data: [
            {
              run_date: "2026-05-07",
              status: "success",
              error_message: null,
            },
          ],
        }),
      } as Response;
    }

    if (url.includes("/api/v1/watchlists/default/tickers")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/alerts/recent")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/kpi")) {
      return {
        json: async () => ({
          data: {
            total_days: 0,
            avg_precision_at_top_n: 0,
            total_screener_views: 0,
            total_alerts_views: 0,
            total_watchlist_views: 0,
          },
        }),
      } as Response;
    }

    return {
      json: async () => ({
        data: [
          { ticker: "BBRI.JK", rank_num: 1, score: 0.91, pass_count: 4, category: "ideal" },
          { ticker: "BBCA.JK", rank_num: 2, score: 0.83, pass_count: 3, category: "candidate" },
        ],
      }),
    } as Response;
  });
}

test("applies terminal shell classes and typography separation hooks", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  const shell = await screen.findByTestId("screener-shell");
  expect(shell.className).toContain("bg-zinc-950");
  expect(shell.className).toContain("text-zinc-100");

  const uiHeading = screen.getByRole("heading", { name: "Fresh ARA Screener" });
  expect(uiHeading.className).toContain("font-ui");

  const dataRow = await screen.findByTestId("screener-row-BBRI.JK");
  expect(dataRow.className).toContain("font-data");
});


test("shows screener title", async () => {
  mockApiResponses();

  render(<ScreenerPage />);
  expect(screen.getByText("Fresh ARA Screener")).toBeInTheDocument();
  expect(await screen.findByTestId("screener-row-BBRI.JK")).toBeInTheDocument();
  expect(screen.getByText("0.91")).toBeInTheDocument();
  expect(screen.getAllByText("ideal").length).toBeGreaterThan(0);
});

test("renders rows from api", async () => {
  mockApiResponses();

  render(<ScreenerPage />);
  expect(await screen.findByTestId("screener-row-BBCA.JK")).toBeInTheDocument();
});

test("shows backtest summary", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Backtest Summary")).toBeInTheDocument();
  expect(screen.getByText("Win rate: 50.00%")).toBeInTheDocument();
  expect(screen.getByText("Average score: 0.81")).toBeInTheDocument();
  expect(screen.getByText("Total samples: 2")).toBeInTheDocument();
});

test("shows export csv link", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  const link = await screen.findByRole("link", { name: "Export CSV" });
  expect(link).toHaveAttribute("href", "/api/v1/export/screener.csv?screen_date=2026-05-07&preset=balanced");
});

test("shows export xlsx link", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  const link = await screen.findByRole("link", { name: "Export XLSX" });
  expect(link).toHaveAttribute("href", "/api/v1/export/screener.xlsx?screen_date=2026-05-07&preset=balanced");
});

test("shows latest daily job status", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Daily Job Status")).toBeInTheDocument();
  expect(screen.getByText("Date: 2026-05-07")).toBeInTheDocument();
  expect(screen.getByText("Status: success")).toBeInTheDocument();
});

test("shows skipped label for non-trading day status", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-09" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [{ preset_name: "balanced" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-09",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({
          data: [
            {
              run_date: "2026-05-10",
              status: "skipped",
              error_message: "no market data",
            },
          ],
        }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.0, avg_score: 0.0, total: 0 } }),
      } as Response;
    }

    return {
      json: async () => ({ data: [{ ticker: "BBRI.JK" }] }),
    } as Response;
  });

  render(<ScreenerPage />);

  expect(await screen.findByText("Daily Job Status")).toBeInTheDocument();
  expect(screen.getByText("Date: 2026-05-10")).toBeInTheDocument();
  expect(screen.getByText("Status: skipped (non-trading day)")).toBeInTheDocument();
  expect(screen.getByText("Error: no market data")).toBeInTheDocument();
});

test("loads default preset and screen date from metadata", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByDisplayValue("balanced")).toBeInTheDocument();
  expect(screen.getByDisplayValue("2026-05-07")).toBeInTheDocument();
});

test("shows data freshness indicator", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Data Freshness")).toBeInTheDocument();
  expect(screen.getByText("Latest screen date: 2026-05-07")).toBeInTheDocument();
});

test("shows probabilistic disclaimer", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Disclaimer")).toBeInTheDocument();
  expect(screen.getByText("Sinyal bersifat probabilistik, bukan jaminan hasil.")).toBeInTheDocument();
});

test("shows data freshness warning when eod is incomplete", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({
          data: [
            { preset_name: "conservative" },
            { preset_name: "balanced" },
            { preset_name: "aggressive" },
          ],
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-07",
            is_complete: false,
            warning: "Data EOD belum complete",
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.5, avg_score: 0.81, total: 2 } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({
          data: [{ run_date: "2026-05-07", status: "success", error_message: null }],
        }),
      } as Response;
    }

    return {
      json: async () => ({ data: [{ ticker: "BBRI.JK" }] }),
    } as Response;
  });

  render(<ScreenerPage />);

  expect(await screen.findByText("Warning: Data EOD belum complete")).toBeInTheDocument();
});

test("falls back safely when metadata endpoints fail", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: null }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({ data: null }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.0, avg_score: 0.0, total: 0 } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    return {
      json: async () => ({ data: [] }),
    } as Response;
  });

  render(<ScreenerPage />);

  expect(await screen.findByText("Fresh ARA Screener")).toBeInTheDocument();
  expect(screen.getByText("Latest screen date: 2026-05-06")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Export CSV" })).toHaveAttribute(
    "href",
    "/api/v1/export/screener.csv?screen_date=2026-05-06&preset=balanced",
  );
});

test("stays stable when screener and analytics endpoints fail", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: null } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({ data: null }),
      } as Response;
    }

    return {
      ok: false,
      status: 404,
      json: async () => ({ error: "not found" }),
    } as Response;
  });

  render(<ScreenerPage />);

  expect(await screen.findByText("Fresh ARA Screener")).toBeInTheDocument();
  expect(screen.getByText("Latest screen date: 2026-05-06")).toBeInTheDocument();
  expect(screen.queryByText("Backtest Summary")).not.toBeInTheDocument();
});

test("applies selected filters to api calls and export link", async () => {
  const calls: string[] = [];

  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    calls.push(url);

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({
          data: [
            { preset_name: "conservative" },
            { preset_name: "balanced" },
            { preset_name: "aggressive" },
          ],
        }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.5, avg_score: 0.81, total: 2 } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({
          data: [{ run_date: "2026-05-07", status: "success", error_message: null }],
        }),
      } as Response;
    }

    return {
      json: async () => ({ data: [{ ticker: "BBRI.JK" }] }),
    } as Response;
  });

  render(<ScreenerPage />);

  fireEvent.change(await screen.findByLabelText("Preset"), { target: { value: "aggressive" } });
  fireEvent.change(screen.getByLabelText("Screen Date"), { target: { value: "2026-05-06" } });
  fireEvent.change(screen.getByLabelText("Backtest Start"), { target: { value: "2026-05-01" } });
  fireEvent.change(screen.getByLabelText("Backtest End"), { target: { value: "2026-05-15" } });

  fireEvent.click(screen.getByRole("button", { name: "Apply Filters" }));

  await waitFor(() => {
    expect(calls.some((url) => url.includes("/api/v1/screener?screen_date=2026-05-06&preset=aggressive"))).toBe(true);
    expect(calls.some((url) => url.includes("/api/v1/analytics/backtest?start=2026-05-01&end=2026-05-15&preset=aggressive"))).toBe(true);
    expect(calls.some((url) => url.includes("/api/v1/meta/job-runs?limit=1"))).toBe(true);
  });

  const link = screen.getByRole("link", { name: "Export CSV" });
  expect(link).toHaveAttribute("href", "/api/v1/export/screener.csv?screen_date=2026-05-06&preset=aggressive");
});


test("loads detail and history when selecting ticker", async () => {
  const calls: string[] = [];

  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    calls.push(url);

    if (url.includes("/api/v1/screener/BBRI.JK/history")) {
      return {
        json: async () => ({ data: [{ screen_date: "2026-05-07", score: 0.9 }] }),
      } as Response;
    }

    if (url.includes("/api/v1/screener/BBRI.JK?")) {
      return {
        json: async () => ({
          data: { ticker: "BBRI.JK", score: 0.9, pass_count: 4, category: "ideal" },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [{ preset_name: "balanced" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-07",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.5, avg_score: 0.8, total: 1 } }),
      } as Response;
    }

    return {
      json: async () => ({
        data: [{ ticker: "BBRI.JK", score: 0.9, rank_num: 1, pass_count: 4, category: "ideal" }],
      }),
    } as Response;
  });

  render(<ScreenerPage />);
  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));

  await waitFor(() => {
    expect(calls.some((url) => url.includes("/api/v1/screener/BBRI.JK?screen_date=2026-05-07&preset=balanced"))).toBe(true);
    expect(calls.some((url) => url.includes("/api/v1/screener/BBRI.JK/history?start=2026-05-01&end=2026-05-31&preset=balanced"))).toBe(true);
  });
});

test("applies selected-row glow and dims non-selected rows", async () => {
  const calls: string[] = [];

  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    calls.push(url);

    if (url.includes("/api/v1/screener/BBRI.JK/history")) {
      return {
        json: async () => ({ data: [{ screen_date: "2026-05-07", score: 0.9 }] }),
      } as Response;
    }

    if (url.includes("/api/v1/screener/BBRI.JK?")) {
      return {
        json: async () => ({
          data: { ticker: "BBRI.JK", score: 0.9, pass_count: 4, category: "ideal" },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({
          data: { win_rate: 0.5, avg_score: 0.81, total: 2 },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [{ preset_name: "balanced" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-07",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    return {
      json: async () => ({ data: [{ ticker: "BBRI.JK" }, { ticker: "BBCA.JK" }] }),
    } as Response;
  });

  render(<ScreenerPage />);

  const selectedRow = await screen.findByTestId("screener-row-BBRI.JK");
  const otherRow = screen.getByTestId("screener-row-BBCA.JK");

  fireEvent.click(selectedRow);

  await waitFor(() => {
    expect(calls.some((url) => url.includes("/api/v1/screener/BBRI.JK?screen_date=2026-05-07&preset=balanced"))).toBe(true);
    expect(calls.some((url) => url.includes("/api/v1/screener/BBRI.JK/history?start=2026-05-01&end=2026-05-31&preset=balanced"))).toBe(true);
  });

  expect(selectedRow.className).toContain("shadow-row-glow");
  expect(selectedRow.className).toContain("border-emerald-400");
  expect(otherRow.className).toContain("opacity-60");
});


test("renders desktop table and mobile card containers", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByTestId("screener-table-section")).toBeInTheDocument();
  expect(screen.getByTestId("screener-card-section")).toBeInTheDocument();
});


test("shows summary metrics strip", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByTestId("summary-strip")).toBeInTheDocument();
  expect(screen.getByText("Total candidates: 2")).toBeInTheDocument();
  expect(screen.getByText("Ideal count: 1")).toBeInTheDocument();
});

test("applies terminal-style classes to summary strip", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  const strip = await screen.findByTestId("summary-strip");
  expect(strip.className).toContain("border-zinc-800");
  expect(strip.className).toContain("bg-zinc-900/50");
});

test("applies terminal-style classes to filter action rail", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  const rail = await screen.findByTestId("filter-action-rail");
  expect(rail.className).toContain("border-zinc-800");
  expect(rail.className).toContain("bg-zinc-900/40");

  const applyButton = screen.getByRole("button", { name: "Apply Filters" });
  expect(applyButton.className).toContain("border-emerald-400");
  expect(applyButton.className).toContain("text-emerald-300");
});

test("shows inline detail panel with selected ticker and score", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/screener/BBRI.JK/history")) {
      return {
        json: async () => ({ data: [{ screen_date: "2026-05-07", score: 0.9 }] }),
      } as Response;
    }

    if (url.includes("/api/v1/screener/BBRI.JK?")) {
      return {
        json: async () => ({
          data: {
            ticker: "BBRI.JK",
            score: 0.9,
            pass_count: 4,
            category: "ideal",
            pass_vol_ratio: 1,
            pass_range_pct: 1,
            pass_price_action: 1,
            pass_is_ara_t0: 1,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [{ preset_name: "balanced" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-07",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.5, avg_score: 0.8, total: 1 } }),
      } as Response;
    }

    return {
      json: async () => ({
        data: [{ ticker: "BBRI.JK", score: 0.9, rank_num: 1, pass_count: 4, category: "ideal" }],
      }),
    } as Response;
  });

  render(<ScreenerPage />);

  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));

  const panel = await screen.findByTestId("inline-detail-panel");
  expect(panel).toBeInTheDocument();
  expect(screen.getByText("Selected: BBRI.JK")).toBeInTheDocument();
  expect(within(panel).getByText("Score: 0.90")).toBeInTheDocument();
  expect(screen.getByText("pass_vol_ratio: 1")).toBeInTheDocument();
  expect(screen.getByText("pass_range_pct: 1")).toBeInTheDocument();
});

test("closes inline detail panel", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));
  expect(await screen.findByTestId("inline-detail-panel")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Close Detail" }));

  await waitFor(() => {
    expect(screen.queryByTestId("inline-detail-panel")).not.toBeInTheDocument();
  });
});

test("applies terminal-style classes to inline detail panel", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));

  const panel = await screen.findByTestId("inline-detail-panel");
  expect(panel.className).toContain("border-zinc-800");
  expect(panel.className).toContain("bg-zinc-900/70");

  const closeButton = screen.getByRole("button", { name: "Close Detail" });
  expect(closeButton.className).toContain("border-zinc-700");
});

test("keeps shell interactive during delayed requests", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    await new Promise((resolve) => setTimeout(resolve, url.includes("/api/v1/screener") ? 80 : 20));

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-07" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [{ preset_name: "balanced" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-07",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.5, avg_score: 0.8, total: 2 } }),
      } as Response;
    }

    return {
      json: async () => ({
        data: [{ ticker: "BBRI.JK", score: 0.9, rank_num: 1, pass_count: 4, category: "ideal" }],
      }),
    } as Response;
  });

  render(<ScreenerPage />);

  expect(screen.getByText("Loading screener...")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Apply Filters" })).toBeEnabled();

  expect(await screen.findByTestId("screener-row-BBRI.JK")).toBeInTheDocument();
  await waitFor(() => {
    expect(screen.queryByText("Loading screener...")).not.toBeInTheDocument();
  });
});

test("shows install-ready hint in ui shell", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Installable PWA ready")).toBeInTheDocument();
});


test("shows watchlist, alerts, and kpi roadmap panels", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/v1/meta/latest-screen-date")) {
      return {
        json: async () => ({ data: { latest_screen_date: "2026-05-21" } }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/presets")) {
      return {
        json: async () => ({ data: [{ preset_name: "balanced" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/data-freshness")) {
      return {
        json: async () => ({
          data: {
            latest_screen_date: "2026-05-21",
            is_complete: true,
            warning: null,
          },
        }),
      } as Response;
    }

    if (url.includes("/api/v1/meta/job-runs")) {
      return {
        json: async () => ({ data: [] }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/backtest")) {
      return {
        json: async () => ({ data: { win_rate: 0.5, avg_score: 0.8, total: 1 } }),
      } as Response;
    }

    if (url.includes("/api/v1/watchlists/default/tickers")) {
      return {
        json: async () => ({ data: [{ watchlist_name: "default", ticker: "BBCA.JK" }] }),
      } as Response;
    }

    if (url.includes("/api/v1/alerts/recent")) {
      return {
        json: async () => ({
          data: [
            {
              run_date: "2026-05-21",
              watchlist_name: "default",
              ticker: "BBCA.JK",
              preset: "balanced",
              created_at: "2026-05-21T18:00:00",
            },
          ],
        }),
      } as Response;
    }

    if (url.includes("/api/v1/analytics/kpi")) {
      return {
        json: async () => ({
          data: {
            total_days: 2,
            avg_precision_at_top_n: 0.75,
            total_screener_views: 18,
            total_alerts_views: 3,
            total_watchlist_views: 5,
          },
        }),
      } as Response;
    }

    return {
      json: async () => ({ data: [{ ticker: "BBCA.JK" }] }),
    } as Response;
  });

  render(<ScreenerPage />);

  const watchlistHeading = await screen.findByText("Watchlist (default)");
  expect(watchlistHeading).toBeInTheDocument();
  expect(screen.getByText("Recent Alerts")).toBeInTheDocument();
  expect(screen.getAllByText("BBCA.JK").length).toBeGreaterThan(0);
  expect(screen.getByText("KPI Baseline")).toBeInTheDocument();
  expect(screen.getByText("Avg Precision@TopN: 0.75")).toBeInTheDocument();
});
