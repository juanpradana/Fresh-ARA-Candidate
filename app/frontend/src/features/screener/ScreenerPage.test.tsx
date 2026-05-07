import { render, screen } from "@testing-library/react";
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
  expect(link).toHaveAttribute("href", "/api/v1/export/screener.csv?preset=balanced");
});

test("shows latest daily job status", async () => {
  mockApiResponses();

  render(<ScreenerPage />);

  expect(await screen.findByText("Daily Job Status")).toBeInTheDocument();
  expect(screen.getByText("Date: 2026-05-07")).toBeInTheDocument();
  expect(screen.getByText("Status: success")).toBeInTheDocument();
});
