import { render, screen } from "@testing-library/react";
import { beforeEach, test, vi } from "vitest";
import { ScreenerPage } from "./ScreenerPage";

beforeEach(() => {
  vi.restoreAllMocks();
});

test("shows screener title", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    json: async () => ({ data: [{ ticker: "BBRI.JK" }] })
  } as Response);

  render(<ScreenerPage />);
  expect(screen.getByText("Fresh ARA Screener")).toBeInTheDocument();
  expect(await screen.findByText("BBRI.JK")).toBeInTheDocument();
});

test("renders rows from api", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    json: async () => ({ data: [{ ticker: "BBCA.JK" }] })
  } as Response);

  render(<ScreenerPage />);
  expect(await screen.findByText("BBCA.JK")).toBeInTheDocument();
});
