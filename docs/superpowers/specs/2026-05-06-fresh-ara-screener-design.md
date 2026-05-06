# Design Spec — Web Screener Fresh ARA Candidate (v1)

Tanggal: 2026-05-06  
Status: Approved for planning

## 1. Scope and Goals

### Goals (v1)
- Deliver end-to-end, usable local application for daily Fresh ARA candidate screening.
- Provide read-only web interface for candidate exploration, filtering, detail view, analytics, and export.
- Run daily screening pipeline at 18:00 WIB with idempotent and retry-safe behavior.

### Locked Decisions
- Frontend stack: React + Vite + TypeScript + PWA.
- Backend stack: FastAPI + APScheduler + SQLite (SQLAlchemy).
- Market data source: Yahoo Finance (`yfinance`) for v1.
- Alerting: deferred to v1.1 (not implemented in v1).
- Deployment target: local-first.

### Out of Scope (v1)
- Auto-trading or order execution.
- UI-triggered market refresh.
- Alert delivery channels (Telegram/email).

## 2. High-Level Architecture

The system is implemented in one repository with modular boundaries and vertical delivery slices.

- Ingestion Layer: CLI commands and scheduled daily job execution.
- Data Layer: SQLite as source of truth, accessed through repositories.
- Domain Layer: reusable services for market data, feature engineering, screening, and scoring.
- Presentation Layer: FastAPI read-only API and React PWA frontend.

### Core Boundaries
- Data mutation is only via CLI/scheduler pipeline.
- API and UI are read-only against screening outputs.
- Shared domain services are consumed by both CLI and API to avoid logic duplication.

## 3. Backend Components and Daily Flow

## 3.1 Modules
- `app/backend/core`
  - `config.py`: app settings (db path, qps, batch size, timezone, retry settings).
  - `db.py`: SQLite engine/session and startup bootstrap.
  - `logging.py`: structured logging for job/api execution.
- `app/backend/repositories/sqlite`
  - Repositories for `tickers`, `prices_daily`, `features_daily`, `screening_results`, `screening_presets`, `job_runs`.
- `app/backend/services`
  - `market_data`: fetch, throttle, batch, retry, dedupe.
  - `feature_engineering`: compute features from EOD data.
  - `screening`: apply rules and pass/fail categorization.
  - `scoring`: score and ranking logic.
- `app/backend/cli`
  - CLI entry and command handlers per PRD.
- `app/backend/scheduler`
  - APScheduler cron job at 18:00 Asia/Jakarta.
- `app/backend/api`
  - Read-only routers under `/api/v1`.

## 3.2 Daily Pipeline (`run-daily --date D`)
1. Acquire job lock.
2. Check idempotent guard in `job_runs` for date D.
3. Run market update (incremental fetch for missing date/ticker rows).
4. Validate EOD completeness for date D.
5. Compute daily features for date D.
6. Run screening with selected preset (default balanced).
7. Persist scored/ranked results.
8. Persist job run status and metadata.
9. Release lock.

## 3.3 Reliability Policies
- Request throttling with configurable QPS.
- Batch fetching by ticker groups.
- Retry with exponential backoff + jitter for 429/5xx.
- Circuit-break pause on repeated failures.
- Incremental updates and dedupe.
- Job lock to prevent concurrent runs.

## 4. Frontend PWA and UX

## 4.1 Main Screens
1. Screener List
   - Candidate table: rank, ticker, score, pass_count, category.
   - Filters: screen date, preset, search, pagination.
   - Rule pass/fail badges.
2. Ticker Detail
   - Indicator values and pass/fail per rule.
   - Screening reason summary.
3. Ticker History
   - Historical signal timeline for date range.
4. Analytics
   - Distribution and backtest summary view.
5. Export
   - CSV/XLSX export with active query parameters.

## 4.2 UX Constraints
- No market refresh button in UI.
- Read/query/export only.
- Freshness indicator and warning when latest data is unavailable.
- Probabilistic-signal disclaimer always visible in relevant pages.

## 4.3 PWA Behavior
- Installable manifest.
- Static asset caching for app shell.
- API data retrieval remains network-first.

## 5. API Contract

Base path: `/api/v1`

- `GET /health`
- `GET /meta/latest-screen-date`
- `GET /meta/presets`
- `GET /screener`
- `GET /screener/{ticker}`
- `GET /screener/{ticker}/history`
- `GET /analytics/distribution`
- `GET /analytics/backtest`
- `GET /export/screener.csv`
- `GET /export/screener.xlsx`

## 5.1 Response Principles
- Consistent envelope:
  - `data`
  - `meta`
  - `error`
- Error statuses:
  - `400` invalid query
  - `404` missing resource
  - `422` validation issue
  - `500` unexpected failure

## 5.2 Data Mapping Notes
- `reason_json` persisted in DB and returned as JSON object in API.
- Export endpoints align with screener query parameters.

## 6. Testing Strategy

## 6.1 Backend Unit Tests
- Screening rule logic and preset boundaries.
- Scoring/ranking determinism.
- Feature formulas (`vol_ratio`, `range_pct`, `price_action`).

## 6.2 Backend Integration Tests
- CLI chain execution on SQLite test DB.
- Idempotency on repeated same-date runs.
- API response contract verification.

## 6.3 Frontend Tests
- Screener rendering, filtering, pagination.
- Ticker detail pass/fail visibility.
- Loading/empty/error states.

## 6.4 E2E Smoke (Local)
- Pipeline run -> open web -> filter -> detail -> export CSV.

## 7. Acceptance Mapping (PRD)

- UAT #1: Balanced preset daily run without error.
- UAT #2: Filter affects results quickly.
- UAT #3: Detail shows indicators and pass/fail.
- UAT #4: Backtest metrics valid by period.
- UAT #6: Freshness warning appears when data incomplete.
- UAT #5 (alert): deferred by decision to v1.1.

## 8. Delivery Milestones (Local-First)

- M1: DB schema + repositories + CLI pipeline.
- M2: FastAPI read-only endpoints complete.
- M3: React PWA screener/detail/analytics/export/freshness flows.
- M4: Test pass, local runbook, UAT checklist completion.

## 9. Risks and Mitigations

- False positives: expose transparent pass flags and category semantics.
- Data lag/incompleteness: freshness gate and warning surfaces.
- Market regime drift: threshold recalibration path maintained via presets.
- Overfitting risk: keep backtest and rolling evaluation endpoints available.

## 10. Implementation Start Criteria

Implementation planning can start when:
- This spec is approved without open ambiguities.
- File/module structure follows PRD boundaries.
- v1 remains strictly read-only with local deployment target.
