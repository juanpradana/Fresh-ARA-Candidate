# Frontend Tailwind Terminal Design Spec

## Goal
Build a high-quality read-only frontend experience for Fresh ARA screening using Tailwind CSS with a professional terminal-inspired visual style, while preserving fast daily decision workflows for desktop and mobile users.

## Scope
This spec covers frontend UX/UI only:
- Screener list, ticker detail, history, analytics summary, export actions
- Data freshness indicator and probabilistic disclaimer
- Mobile-friendly behavior and installable PWA readiness

Out of scope:
- Trading actions
- Market data refresh controls in UI
- Backend contract changes beyond existing API

## Locked Product Decisions
- Visual style: professional terminal-inspired (dark, sharp, data-dense)
- Layout strategy: balanced (compact summary + table-dominant core)
- Density strategy: adaptive (desktop compact, mobile comfortable)
- Detail interaction: inline drawer/modal from screener list
- Mobile list mode: card list per ticker (no horizontal table scroll)

## Information Architecture

### Desktop
1. Top bar
   - Brand/title
   - Latest screen date
   - Freshness badge/warning
   - Preset selector
2. Summary strip (compact)
   - Total candidates
   - Ideal count
   - Top score
   - Latest job status
3. Main screener area
   - Primary: screener table (rank, ticker, score, pass_count, category)
   - Secondary rail: filter date controls, export actions, backtest summary
4. Detail drawer
   - Opens from selected row without leaving list context
5. Footer notice
   - Probabilistic disclaimer

### Mobile
1. Top bar + summary strip remain
2. Screener content rendered as ticker cards
3. Detail opened in bottom-sheet style drawer/modal
4. Filter/export actions placed in accessible action area

## Data Mapping (API Contracts)
- `GET /api/v1/meta/latest-screen-date`
- `GET /api/v1/meta/data-freshness`
- `GET /api/v1/meta/presets`
- `GET /api/v1/meta/job-runs?limit=1`
- `GET /api/v1/screener?screen_date=...&preset=...&limit=...&offset=...`
- `GET /api/v1/screener/{ticker}?screen_date=...&preset=...`
- `GET /api/v1/screener/{ticker}/history?start=...&end=...&preset=...`
- `GET /api/v1/analytics/backtest?start=...&end=...&preset=...`
- `GET /api/v1/export/screener.csv?screen_date=...&preset=...`
- `GET /api/v1/export/screener.xlsx?screen_date=...&preset=...`

## Visual System (Tailwind)

### Palette and surfaces
- Dark neutral base backgrounds for terminal tone
- High-contrast text hierarchy for dense data reading
- Semantic accents:
  - success/ideal: emerald family
  - candidate: amber family
  - warning/freshness incomplete: orange-red family
  - failure: red family
- Surfaces: subtle contrast elevation + thin borders (no heavy glass effects)

### Typography and spacing
- UI typography and data typography are explicitly separated.
- UI text (headings, labels, helper text) uses a clean sans-serif stack for readability.
- Data text (rank, ticker code, score, pass_count, percentages, status metrics) uses a monospace/tabular stack for scan speed and vertical alignment.
- Numeric emphasis remains tabular-aligned for fast comparison.
- Spacing scale kept consistent and minimal to support dense tables

### Interactive states
- Strong keyboard focus rings
- Clear row hover and selected states before drawer open
- Selected row uses a subtle border-glow accent to anchor focus.
- Non-selected rows use mild dimming when a selection is active, preserving context while emphasizing the active ticker.
- Lightweight skeleton/loading states and deterministic empty states

## Component Blueprint

### `ScreenerShell`
Owns global UI state:
- filters (preset, screen_date, backtest start/end)
- selected ticker
- drawer open/close
- loading/error states per data block

### `TopBar`
Uses metadata endpoints for latest date, freshness, preset selection.

### `SummaryStrip`
Displays total candidates, ideal count, top score, latest job status.

### `ScreenerTableSection` (desktop)
- Sticky header
- Compact rows
- Pagination controls
- Row click opens detail drawer

### `ScreenerCardListSection` (mobile)
- Comfortable card spacing
- Core fields only for fast scan
- Tap opens bottom-sheet detail

### `ActionRail` / `BottomActions`
- Date and preset controls
- Apply action
- Export CSV/XLSX
- Backtest summary display

### `TickerDetailDrawer`
- Ticker, score, category summary
- Rule pass/fail chips
- Reason payload summary
- History list for selected period

### `GlobalNoticeBar`
- Freshness warning when incomplete
- Persistent probabilistic disclaimer

## Interaction Flow
1. Initial load fetches latest-screen-date, presets, freshness.
2. Defaults are resolved and stored in filter state.
3. Screener rows, backtest summary, and latest job status load in parallel.
4. Changing filters triggers deterministic re-fetch.
5. Selecting a ticker opens detail drawer and fetches detail/history.
6. Export URLs are always derived from active filters.

## Error and Empty-State Strategy
- Metadata failure: safe defaults for preset/date.
- Screener empty: show actionable empty state (adjust filters).
- Detail/history failure: drawer remains open with inline retry affordance.
- Backtest failure: suppress summary block, keep screener usable.

## Testing Strategy

### Frontend tests (Vitest + Testing Library)
- Render coverage for loading/success/empty/error
- Filter state and request query composition
- Desktop table and mobile card rendering
- Drawer open + detail/history rendering
- Freshness warning and disclaimer visibility
- Export URL composition from active filters
- Latency simulation coverage: delayed responses for screener/meta/detail/history/backtest to verify loading states, non-blocking partial render, and stable interaction under slow network conditions

### Backend regression continuity
- Keep `pytest -q` green as API contract safety net while frontend evolves

## PRD Acceptance Mapping
1. Balanced preset yields daily candidates without UI errors.
2. Filter changes update results quickly and consistently.
3. Detail view shows indicator pass/fail status clearly.
4. Backtest summary reflects selected date range.
5. Freshness warning is visible when data is incomplete.
6. Read-only scope preserved (no market refresh action, no trading action).
7. Mobile-friendly experience delivered with installable readiness.

## Implementation Slices
1. Tailwind foundation and terminal theme tokens
2. Screener core view (desktop table + mobile cards)
3. Detail drawer + history
4. Analytics summary + export rail
5. Polish: PWA shell, accessibility, regression hardening

## Risks and Mitigations
- Risk: visual density hurts readability
  - Mitigation: adaptive density and strict typography contrast rules
- Risk: drawer state complexity causes UI inconsistency
  - Mitigation: single-source state in shell + explicit open/close transitions
- Risk: endpoint failures degrade whole page
  - Mitigation: independent block-level fallbacks and graceful partial rendering

## Success Criteria
- Users can complete daily screening and inspect details without leaving screener context.
- UI stays fast, legible, and read-only across desktop and mobile.
- Data freshness and disclaimer are always visible and understandable.
- All relevant frontend and backend tests pass before release.
