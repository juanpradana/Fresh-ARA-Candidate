import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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

    return {
      json: async () => ({ data: [{ ticker: "BBRI.JK" }, { ticker: "BBCA.JK" }] }),
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
  expect(await screen.findByText("BBRI.JK")).toBeInTheDocument();
});

test("renders rows from api", async () => {
  mockApiResponses();

  render(<ScreenerPage />);
  expect(await screen.findByText("BBCA.JK")).toBeInTheDocument();
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
