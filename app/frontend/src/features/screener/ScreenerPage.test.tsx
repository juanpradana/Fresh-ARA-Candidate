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
  expect(link).toHaveAttribute("href", "/api/v1/export/screener.csv?screen_date=2026-05-06&preset=balanced");
});

test("shows latest daily job status", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Daily Job Status")).toBeInTheDocument();
  expect(screen.getByText("Date: 2026-05-07")).toBeInTheDocument();
  expect(screen.getByText("Status: success")).toBeInTheDocument();
});

test("applies selected filters to api calls and export link", async () => {
  const calls: string[] = [];

  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    calls.push(url);

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
