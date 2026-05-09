# Frontend Tailwind Terminal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready read-only screener UI using Tailwind with terminal-inspired styling, adaptive desktop/mobile layouts, inline ticker detail drawer, and robust latency-aware UX.

**Architecture:** Keep a single page entry (`ScreenerPage`) as orchestration shell, then split render responsibilities into focused presentational components under `features/screener/components`. Keep all API I/O in `shared/api/client.ts` and normalize response shapes there so UI components can stay simple. Use Tailwind utility classes and small helper constants for theme, typography separation (UI vs data), and selected-row glow/dimming behavior.

**Tech Stack:** React 18, TypeScript, Vite, Vitest + Testing Library, Tailwind CSS, vite-plugin-pwa

---

## Execution Status (Updated)

- [x] Task 1: Install Tailwind Foundation and Global Theme
- [x] Task 2: Refactor API Client for Full Screener Surface
- [x] Task 3: Build Shell + Desktop Table + Mobile Cards
- [x] Task 4: Add Action Rail, Export, Freshness, and Disclaimer
- [x] Task 5: Implement Inline Ticker Detail Drawer with History
- [x] Task 6: Add Latency Simulation and Slow-Network UX Guards
- [x] Task 7: PWA Polish and Final Regression

## File Structure Map

- Modify: `app/frontend/package.json`
  - Add Tailwind/PostCSS tooling scripts/deps only.
- Create: `app/frontend/postcss.config.js`
  - Wire Tailwind PostCSS plugin.
- Create: `app/frontend/tailwind.config.ts`
  - Theme tokens, semantic colors, font families, shadows.
- Create: `app/frontend/src/styles/tailwind.css`
  - Tailwind directives and global terminal-inspired base styles.
- Modify: `app/frontend/src/main.tsx`
  - Import global Tailwind stylesheet.
- Modify: `app/frontend/src/shared/api/client.ts`
  - Expand types and functions for distribution/detail/history plus normalized helpers.
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
  - Convert into shell state orchestrator and compose child components.
- Create: `app/frontend/src/features/screener/components/ScreenerTopBar.tsx`
- Create: `app/frontend/src/features/screener/components/SummaryStrip.tsx`
- Create: `app/frontend/src/features/screener/components/ScreenerTableSection.tsx`
- Create: `app/frontend/src/features/screener/components/ScreenerCardListSection.tsx`
- Create: `app/frontend/src/features/screener/components/ActionRail.tsx`
- Create: `app/frontend/src/features/screener/components/TickerDetailDrawer.tsx`
- Create: `app/frontend/src/features/screener/components/GlobalNoticeBar.tsx`
- Modify: `app/frontend/src/features/screener/ScreenerPage.test.tsx`
  - Add RED/GREEN tests for each behavior slice.
- Modify: `app/frontend/vite.config.ts`
  - Tailwind-compatible CSS pipeline stays implicit; update PWA manifest visuals for dark theme only if needed by tests.

---

### Task 1: Install Tailwind Foundation and Global Theme

**Files:**
- Modify: `app/frontend/package.json`
- Create: `app/frontend/postcss.config.js`
- Create: `app/frontend/tailwind.config.ts`
- Create: `app/frontend/src/styles/tailwind.css`
- Modify: `app/frontend/src/main.tsx`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
// add to ScreenerPage.test.tsx
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "applies terminal shell classes and typography separation hooks"`
Expected: FAIL (missing class hooks/test ids).

- [ ] **Step 3: Write minimal implementation**

```ts
// package.json (devDependencies additions)
"tailwindcss": "^3.4.17",
"postcss": "^8.4.49",
"autoprefixer": "^10.4.20"
```

```js
// postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        ui: ["Inter", "system-ui", "sans-serif"],
        data: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        "row-glow": "0 0 0 1px rgba(16,185,129,0.8), 0 0 14px rgba(16,185,129,0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
```

```css
/* src/styles/tailwind.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-zinc-950 text-zinc-100 font-ui;
  }
}
```

```tsx
// main.tsx
import "./styles/tailwind.css";
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "applies terminal shell classes and typography separation hooks"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/package.json app/frontend/postcss.config.js app/frontend/tailwind.config.ts app/frontend/src/styles/tailwind.css app/frontend/src/main.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: add tailwind terminal theme foundation"
```

---

### Task 2: Refactor API Client for Full Screener Surface

**Files:**
- Modify: `app/frontend/src/shared/api/client.ts`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
test("loads detail and history when selecting ticker", async () => {
  const calls: string[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    calls.push(url);

    if (url.includes("/api/v1/screener/BBRI.JK/history")) {
      return { json: async () => ({ data: [{ screen_date: "2026-05-07", score: 0.9 }] }) } as Response;
    }

    if (url.includes("/api/v1/screener/BBRI.JK?")) {
      return { json: async () => ({ data: { ticker: "BBRI.JK", score: 0.9, pass_count: 4, category: "ideal" } }) } as Response;
    }

    if (url.includes("/api/v1/meta/latest-screen-date")) return { json: async () => ({ data: { latest_screen_date: "2026-05-07" } }) } as Response;
    if (url.includes("/api/v1/meta/presets")) return { json: async () => ({ data: [{ preset_name: "balanced" }] }) } as Response;
    if (url.includes("/api/v1/meta/data-freshness")) return { json: async () => ({ data: { latest_screen_date: "2026-05-07", is_complete: true, warning: null } }) } as Response;
    if (url.includes("/api/v1/meta/job-runs")) return { json: async () => ({ data: [] }) } as Response;
    if (url.includes("/api/v1/analytics/backtest")) return { json: async () => ({ data: { win_rate: 0.5, avg_score: 0.8, total: 1 } }) } as Response;

    return { json: async () => ({ data: [{ ticker: "BBRI.JK", score: 0.9, rank_num: 1, pass_count: 4, category: "ideal" }] }) } as Response;
  });

  render(<ScreenerPage />);
  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));

  await waitFor(() => {
    expect(calls.some((url) => url.includes("/api/v1/screener/BBRI.JK?screen_date=2026-05-07&preset=balanced"))).toBe(true);
    expect(calls.some((url) => url.includes("/api/v1/screener/BBRI.JK/history?start=2026-05-01&end=2026-05-31&preset=balanced"))).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "loads detail and history when selecting ticker"`
Expected: FAIL (no detail/history API calls yet).

- [ ] **Step 3: Write minimal implementation**

```ts
// client.ts additions (types)
export type ScreenerRow = {
  ticker: string;
  rank_num?: number;
  score?: number;
  pass_count?: number;
  category?: string;
};

export type ScreenerDetail = {
  ticker: string;
  score?: number;
  pass_count?: number;
  category?: string;
  pass_vol_ratio?: number;
  pass_range_pct?: number;
  pass_price_action?: number;
  pass_is_ara_t0?: number;
  reason_json?: string | null;
} | null;

export type ScreenerHistoryRow = {
  screen_date?: string;
  score?: number;
  pass_count?: number;
  category?: string;
};

export async function getScreenerDetail(params: { ticker: string; screenDate: string; preset: string }): Promise<ScreenerDetail> {
  try {
    const qs = new URLSearchParams({ screen_date: params.screenDate, preset: params.preset });
    const res = await fetch(`/api/v1/screener/${params.ticker}?${qs.toString()}`);
    const json = await res.json();
    return json?.data ?? null;
  } catch {
    return null;
  }
}

export async function getScreenerHistory(params: { ticker: string; start: string; end: string; preset: string }): Promise<ScreenerHistoryRow[]> {
  try {
    const qs = new URLSearchParams({ start: params.start, end: params.end, preset: params.preset });
    const res = await fetch(`/api/v1/screener/${params.ticker}/history?${qs.toString()}`);
    const json = await res.json();
    return Array.isArray(json?.data) ? json.data : [];
  } catch {
    return [];
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "loads detail and history when selecting ticker"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/src/shared/api/client.ts app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: add screener detail and history api client"
```

---

### Task 3: Build Shell + Desktop Table + Mobile Cards

**Files:**
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Create: `app/frontend/src/features/screener/components/ScreenerTopBar.tsx`
- Create: `app/frontend/src/features/screener/components/SummaryStrip.tsx`
- Create: `app/frontend/src/features/screener/components/ScreenerTableSection.tsx`
- Create: `app/frontend/src/features/screener/components/ScreenerCardListSection.tsx`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing tests**

```tsx
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
  expect(screen.getByText(/Total candidates:/)).toBeInTheDocument();
  expect(screen.getByText(/Ideal count:/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "renders desktop table and mobile card containers|shows summary metrics strip"`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// ScreenerPage.tsx (shell outline)
<div data-testid="screener-shell" className="min-h-screen bg-zinc-950 text-zinc-100">
  <ScreenerTopBar ... />
  <SummaryStrip data-testid="summary-strip" ... />
  <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-4">
    <ScreenerTableSection rows={rows} selectedTicker={selectedTicker} onSelect={setSelectedTicker} />
    <ActionRail ... />
  </div>
  <ScreenerCardListSection rows={rows} selectedTicker={selectedTicker} onSelect={setSelectedTicker} />
</div>
```

```tsx
// ScreenerTableSection.tsx (row class includes font-data)
<tr
  data-testid={`screener-row-${row.ticker}`}
  className={`font-data ${isSelected ? "shadow-row-glow" : selectedTicker ? "opacity-55" : "opacity-100"}`}
>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "renders desktop table and mobile card containers|shows summary metrics strip"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/screener/components/ScreenerTopBar.tsx app/frontend/src/features/screener/components/SummaryStrip.tsx app/frontend/src/features/screener/components/ScreenerTableSection.tsx app/frontend/src/features/screener/components/ScreenerCardListSection.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: add screener shell with adaptive table and cards"
```

---

### Task 4: Add Action Rail, Export, Freshness, and Disclaimer

**Files:**
- Create: `app/frontend/src/features/screener/components/ActionRail.tsx`
- Create: `app/frontend/src/features/screener/components/GlobalNoticeBar.tsx`
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing tests**

```tsx
test("shows freshness warning and disclaimer in global notice", async () => {
  // mock freshness incomplete
  render(<ScreenerPage />);
  expect(await screen.findByText(/Data EOD belum complete/)).toBeInTheDocument();
  expect(screen.getByText("Sinyal bersifat probabilistik, bukan jaminan hasil.")).toBeInTheDocument();
});

test("builds csv/xlsx export links from active filters", async () => {
  mockApiResponses();
  render(<ScreenerPage />);
  fireEvent.change(await screen.findByLabelText("Preset"), { target: { value: "aggressive" } });
  fireEvent.change(screen.getByLabelText("Screen Date"), { target: { value: "2026-05-06" } });

  const csv = screen.getByRole("link", { name: "Export CSV" });
  const xlsx = screen.getByRole("link", { name: "Export XLSX" });

  expect(csv).toHaveAttribute("href", "/api/v1/export/screener.csv?screen_date=2026-05-06&preset=aggressive");
  expect(xlsx).toHaveAttribute("href", "/api/v1/export/screener.xlsx?screen_date=2026-05-06&preset=aggressive");
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "shows freshness warning and disclaimer in global notice|builds csv/xlsx export links from active filters"`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// GlobalNoticeBar.tsx
export function GlobalNoticeBar({ warning }: { warning: string | null }) {
  return (
    <section className="rounded-md border border-zinc-700 bg-zinc-900/80 p-3">
      {warning && <p className="text-amber-300">Warning: {warning}</p>}
      <p className="text-zinc-300">Sinyal bersifat probabilistik, bukan jaminan hasil.</p>
    </section>
  );
}
```

```tsx
// ActionRail.tsx
<a href={getScreenerCsvExportUrl({ screenDate, preset })}>Export CSV</a>
<a href={getScreenerXlsxExportUrl({ screenDate, preset })}>Export XLSX</a>
```

```ts
// client.ts
export function getScreenerXlsxExportUrl(filters: Pick<ScreenerFilters, "screenDate" | "preset">): string {
  const params = new URLSearchParams({ screen_date: filters.screenDate, preset: filters.preset });
  return `/api/v1/export/screener.xlsx?${params.toString()}`;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "shows freshness warning and disclaimer in global notice|builds csv/xlsx export links from active filters"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/src/features/screener/components/ActionRail.tsx app/frontend/src/features/screener/components/GlobalNoticeBar.tsx app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/shared/api/client.ts app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: add action rail exports and global notice"
```

---

### Task 5: Implement Inline Ticker Detail Drawer with History

**Files:**
- Create: `app/frontend/src/features/screener/components/TickerDetailDrawer.tsx`
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing tests**

```tsx
test("opens detail drawer and renders pass/fail chips", async () => {
  // mocks return pass flags on detail endpoint
  render(<ScreenerPage />);

  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));
  expect(await screen.findByTestId("ticker-detail-drawer")).toBeInTheDocument();
  expect(screen.getByText("pass_vol_ratio: 1")).toBeInTheDocument();
  expect(screen.getByText("pass_range_pct: 1")).toBeInTheDocument();
});

test("applies selected row glow and dims non-selected rows", async () => {
  mockApiResponses();
  render(<ScreenerPage />);

  fireEvent.click(await screen.findByTestId("screener-row-BBRI.JK"));

  const selected = screen.getByTestId("screener-row-BBRI.JK");
  const other = screen.getByTestId("screener-row-BBCA.JK");

  expect(selected.className).toContain("shadow-row-glow");
  expect(other.className).toContain("opacity-55");
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "opens detail drawer and renders pass/fail chips|applies selected row glow and dims non-selected rows"`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// TickerDetailDrawer.tsx
export function TickerDetailDrawer({ open, detail, history, onClose }: Props) {
  if (!open) return null;
  return (
    <aside data-testid="ticker-detail-drawer" className="fixed right-0 top-0 h-full w-full max-w-md border-l border-zinc-700 bg-zinc-950 p-4">
      <button onClick={onClose}>Close</button>
      {detail ? (
        <>
          <h3 className="font-data">{detail.ticker}</h3>
          <p>pass_vol_ratio: {detail.pass_vol_ratio ?? 0}</p>
          <p>pass_range_pct: {detail.pass_range_pct ?? 0}</p>
          <p>pass_price_action: {detail.pass_price_action ?? 0}</p>
          <p>pass_is_ara_t0: {detail.pass_is_ara_t0 ?? 0}</p>
          <ul>{history.map((row, idx) => <li key={`${row.screen_date}-${idx}`}>{row.screen_date} {row.score ?? "-"}</li>)}</ul>
        </>
      ) : (
        <p>Detail unavailable</p>
      )}
    </aside>
  );
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "opens detail drawer and renders pass/fail chips|applies selected row glow and dims non-selected rows"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/src/features/screener/components/TickerDetailDrawer.tsx app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: add inline ticker detail drawer with selection states"
```

---

### Task 6: Add Latency Simulation and Slow-Network UX Guards

**Files:**
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Modify: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
test("keeps shell interactive during delayed requests", async () => {
  vi.useFakeTimers();

  vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    await new Promise((resolve) => setTimeout(resolve, url.includes("/api/v1/screener") ? 1200 : 300));

    if (url.includes("/api/v1/meta/latest-screen-date")) return { json: async () => ({ data: { latest_screen_date: "2026-05-07" } }) } as Response;
    if (url.includes("/api/v1/meta/presets")) return { json: async () => ({ data: [{ preset_name: "balanced" }] }) } as Response;
    if (url.includes("/api/v1/meta/data-freshness")) return { json: async () => ({ data: { latest_screen_date: "2026-05-07", is_complete: true, warning: null } }) } as Response;
    if (url.includes("/api/v1/meta/job-runs")) return { json: async () => ({ data: [] }) } as Response;
    if (url.includes("/api/v1/analytics/backtest")) return { json: async () => ({ data: { win_rate: 0.5, avg_score: 0.8, total: 2 } }) } as Response;
    return { json: async () => ({ data: [{ ticker: "BBRI.JK", score: 0.9, rank_num: 1, pass_count: 4, category: "ideal" }] }) } as Response;
  });

  render(<ScreenerPage />);

  expect(screen.getByText("Loading screener...")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Apply Filters" })).toBeEnabled();

  await vi.advanceTimersByTimeAsync(1500);
  expect(await screen.findByText("BBRI.JK")).toBeInTheDocument();

  vi.useRealTimers();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "keeps shell interactive during delayed requests"`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// in ScreenerPage.tsx
const [isLoadingRows, setIsLoadingRows] = useState(false);

const loadRows = async (...) => {
  setIsLoadingRows(true);
  const result = await getScreener(...);
  setRows(result);
  setIsLoadingRows(false);
};

{isLoadingRows && <p>Loading screener...</p>}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "keeps shell interactive during delayed requests"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "test: add latency simulation coverage for screener shell"
```

---

### Task 7: PWA Polish and Final Regression

**Files:**
- Modify: `app/frontend/vite.config.ts`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
// add smoke-like assertion in existing tests for install prompt hint element if implemented
test("shows install-ready hint in ui shell", async () => {
  mockApiResponses();
  render(<ScreenerPage />);
  expect(await screen.findByText("Installable PWA ready")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix app/frontend test -- ScreenerPage.test.tsx -t "shows install-ready hint in ui shell"`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```ts
// vite.config.ts manifest dark polish
manifest: {
  name: "Fresh ARA Screener",
  short_name: "ARA Screener",
  start_url: "/",
  display: "standalone",
  background_color: "#09090b",
  theme_color: "#09090b",
  icons: []
}
```

```tsx
// ScreenerPage.tsx
<p className="text-xs text-zinc-400">Installable PWA ready</p>
```

- [ ] **Step 4: Run verification commands**

Run: `npm --prefix app/frontend test`
Expected: PASS

Run: `npm --prefix app/frontend build`
Expected: PASS

Run: `pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/frontend/vite.config.ts app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: finalize pwa-ready screener shell polish"
```

---

## Plan Self-Review

### 1) Spec coverage check
- Tailwind terminal theme + typography split: Task 1.
- Balanced layout with summary + table/core + action rail: Tasks 3 and 4.
- Desktop table and mobile card list: Task 3.
- Inline detail drawer + history: Task 5.
- Border-glow selected row + dimming non-selected rows: Task 5.
- Freshness warning + disclaimer: Task 4.
- Export CSV/XLSX with active filters: Task 4.
- Latency simulation strategy: Task 6.
- PWA readiness: Task 7.
- Regression discipline (frontend + backend): Task 7.

No spec gaps found.

### 2) Placeholder scan
- Removed TODO/TBD style language.
- Each task has explicit file paths, failing tests, commands, expected outputs, and commit commands.

### 3) Type consistency check
- Shared filter keys: `screenDate`, `preset`, `start`, `end` used consistently.
- Detail/history function names: `getScreenerDetail`, `getScreenerHistory` used consistently across tasks.
- Row identifiers and test ids use `screener-row-${ticker}` consistently.

No naming/type conflicts found.
