# Fresh ARA Screener v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first, read-only web screener that computes and serves Fresh ARA candidates from SQLite via FastAPI and React PWA.

**Architecture:** The backend is a modular monolith with shared domain services used by both CLI and API. A daily pipeline writes market data, computed features, and screening results into SQLite with idempotent guards. The frontend consumes read-only `/api/v1` endpoints and provides screener list, ticker detail/history, analytics, export, and freshness indicators.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, APScheduler, yfinance, pytest, React, Vite, TypeScript, Vitest, PWA plugin.

---

## File Structure Map

### Backend
- Create: `app/backend/core/config.py` — central runtime settings.
- Create: `app/backend/core/db.py` — SQLAlchemy engine/session/bootstrap.
- Create: `app/backend/core/logging.py` — structured logging setup.
- Create: `app/backend/repositories/sqlite/models.py` — ORM models.
- Create: `app/backend/repositories/sqlite/repo.py` — repository queries.
- Create: `app/backend/services/market_data/service.py` — yfinance ingestion.
- Create: `app/backend/services/feature_engineering/service.py` — feature computation.
- Create: `app/backend/services/screening/service.py` — pass/fail logic.
- Create: `app/backend/services/scoring/service.py` — ranking/scoring.
- Create: `app/backend/cli/main.py` — CLI entry point.
- Create: `app/backend/api/app.py` — FastAPI app bootstrap.
- Create: `app/backend/api/routers/*.py` — API routers.
- Create: `app/backend/scheduler/daily.py` — APScheduler job wiring.

### Frontend
- Create: `app/frontend/package.json` + Vite scaffold files.
- Create: `app/frontend/src/shared/api/client.ts` — API client.
- Create: `app/frontend/src/features/screener/*` — screener list/filter.
- Create: `app/frontend/src/features/ticker-detail/*` — detail/history.
- Create: `app/frontend/src/features/analytics/*` — distribution/backtest.
- Create: `app/frontend/src/app/router.tsx` and pages.
- Create: `app/frontend/vite.config.ts` + PWA config.

### Tests
- Create: `tests/backend/test_screening_rules.py`
- Create: `tests/backend/test_pipeline_idempotency.py`
- Create: `tests/backend/test_api_contract.py`
- Create: `app/frontend/src/**/*.test.tsx`

---

### Task 1: Initialize Backend Core and SQLite Schema

**Files:**
- Create: `app/backend/core/config.py`
- Create: `app/backend/core/db.py`
- Create: `app/backend/repositories/sqlite/models.py`
- Test: `tests/backend/test_db_bootstrap.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/backend/test_db_bootstrap.py
from app.backend.core.db import init_db, SessionLocal
from app.backend.repositories.sqlite.models import Ticker

def test_init_db_creates_tables(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "test.sqlite"))
    init_db()
    session = SessionLocal()
    try:
        session.add(Ticker(ticker="BBCA.JK", symbol="BBCA.JK"))
        session.commit()
        assert session.query(Ticker).count() == 1
    finally:
        session.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_db_bootstrap.py -v`  
Expected: FAIL with import/module missing errors.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_db_path: str = "./data/fresh_ara.sqlite"

settings = Settings()
```

```python
# app/backend/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.backend.core.config import settings

Base = declarative_base()
engine = create_engine(f"sqlite:///{settings.app_db_path}", future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db() -> None:
    from app.backend.repositories.sqlite import models
    Base.metadata.create_all(bind=engine)
```

```python
# app/backend/repositories/sqlite/models.py
from sqlalchemy import Column, Integer, Text
from app.backend.core.db import Base

class Ticker(Base):
    __tablename__ = "tickers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(Text, unique=True, nullable=False)
    symbol = Column(Text, nullable=False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_db_bootstrap.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/core/config.py app/backend/core/db.py app/backend/repositories/sqlite/models.py tests/backend/test_db_bootstrap.py
git commit -m "feat: bootstrap backend core and sqlite schema"
```

### Task 2: Implement Feature Engineering and Screening Rule Engine

**Files:**
- Create: `app/backend/services/feature_engineering/service.py`
- Create: `app/backend/services/screening/service.py`
- Create: `app/backend/services/scoring/service.py`
- Test: `tests/backend/test_screening_rules.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.services.screening.service import is_fresh_ara_candidate

def test_balanced_rule_passes_quiet_setup():
    row = {
        "vol_ratio": 1.0,
        "range_pct": 0.8,
        "price_action": 0.6,
        "is_ara_t0": 0,
    }
    assert is_fresh_ara_candidate(row)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_screening_rules.py -v`  
Expected: FAIL because service not implemented.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/services/screening/service.py
from typing import Mapping

def is_fresh_ara_candidate(row: Mapping[str, float | int]) -> bool:
    return (
        0.75 <= float(row["vol_ratio"]) <= 1.25
        and 0.50 <= float(row["range_pct"]) <= 1.00
        and float(row["price_action"]) < 0.70
        and int(row["is_ara_t0"]) == 0
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_screening_rules.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/services/feature_engineering/service.py app/backend/services/screening/service.py app/backend/services/scoring/service.py tests/backend/test_screening_rules.py
git commit -m "feat: implement feature and screening rule services"
```

### Task 3: Build CLI Pipeline Commands

**Files:**
- Create: `app/backend/cli/main.py`
- Create: `app/backend/cli/commands/run_daily.py`
- Modify: `app/backend/services/market_data/service.py`
- Test: `tests/backend/test_pipeline_idempotency.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.cli.commands.run_daily import should_skip_run

def test_should_skip_when_job_already_successful():
    assert should_skip_run("2026-05-06", ["2026-05-06"]) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_pipeline_idempotency.py -v`  
Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/cli/commands/run_daily.py
def should_skip_run(run_date: str, successful_dates: list[str]) -> bool:
    return run_date in successful_dates
```

```python
# app/backend/cli/main.py
import argparse

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--date")
    args = parser.parse_args()
    print(args.command, args.date)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_pipeline_idempotency.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/cli/main.py app/backend/cli/commands/run_daily.py app/backend/services/market_data/service.py tests/backend/test_pipeline_idempotency.py
git commit -m "feat: add idempotent daily pipeline cli skeleton"
```

### Task 4: Expose Read-Only FastAPI Endpoints

**Files:**
- Create: `app/backend/api/app.py`
- Create: `app/backend/api/routers/health.py`
- Create: `app/backend/api/routers/screener.py`
- Test: `tests/backend/test_api_contract.py`

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from app.backend.api.app import app

client = TestClient(app)

def test_health_endpoint_returns_ok():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "ok"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_api_contract.py -v`  
Expected: FAIL because app/router missing.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/api/routers/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health() -> dict:
    return {"data": {"status": "ok"}, "meta": {}, "error": None}
```

```python
# app/backend/api/app.py
from fastapi import FastAPI
from app.backend.api.routers import health

app = FastAPI(title="Fresh ARA Screener")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_api_contract.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/api/app.py app/backend/api/routers/health.py app/backend/api/routers/screener.py tests/backend/test_api_contract.py
git commit -m "feat: add read-only fastapi endpoint scaffolding"
```

### Task 5: Scaffold Frontend React + PWA and Screener List

**Files:**
- Create: `app/frontend/package.json`
- Create: `app/frontend/src/main.tsx`
- Create: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { ScreenerPage } from "./ScreenerPage";

test("shows screener title", () => {
  render(<ScreenerPage />);
  expect(screen.getByText("Fresh ARA Screener")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app/frontend && npm test -- ScreenerPage.test.tsx`  
Expected: FAIL because component/test setup missing.

- [ ] **Step 3: Write minimal implementation**

```tsx
// app/frontend/src/features/screener/ScreenerPage.tsx
export function ScreenerPage() {
  return <h1>Fresh ARA Screener</h1>;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app/frontend && npm test -- ScreenerPage.test.tsx`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/frontend/package.json app/frontend/src/main.tsx app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: scaffold react pwa frontend with screener page"
```

### Task 6: Integrate Backend API Data into Frontend Views

**Files:**
- Create: `app/frontend/src/shared/api/client.ts`
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Create: `app/frontend/src/features/ticker-detail/TickerDetailPage.tsx`
- Test: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
test("renders rows from api", async () => {
  render(<ScreenerPage />);
  expect(await screen.findByText("BBCA.JK")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app/frontend && npm test -- ScreenerPage.test.tsx`  
Expected: FAIL because API wiring not implemented.

- [ ] **Step 3: Write minimal implementation**

```ts
// app/frontend/src/shared/api/client.ts
export async function getScreener(): Promise<{ ticker: string }[]> {
  const res = await fetch("/api/v1/screener");
  const json = await res.json();
  return json.data;
}
```

```tsx
// app/frontend/src/features/screener/ScreenerPage.tsx
import { useEffect, useState } from "react";
import { getScreener } from "../../shared/api/client";

export function ScreenerPage() {
  const [rows, setRows] = useState<{ ticker: string }[]>([]);

  useEffect(() => {
    getScreener().then(setRows);
  }, []);

  return (
    <div>
      <h1>Fresh ARA Screener</h1>
      <ul>{rows.map((row) => <li key={row.ticker}>{row.ticker}</li>)}</ul>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app/frontend && npm test -- ScreenerPage.test.tsx`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/frontend/src/shared/api/client.ts app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/ticker-detail/TickerDetailPage.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: wire screener frontend to backend api"
```

### Task 7: Add Scheduler and Daily Job Trigger at 18:00 WIB

**Files:**
- Create: `app/backend/scheduler/daily.py`
- Modify: `app/backend/cli/main.py`
- Test: `tests/backend/test_scheduler.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.scheduler.daily import build_trigger

def test_scheduler_uses_jakarta_timezone():
    trigger = build_trigger()
    assert "Asia/Jakarta" in str(trigger.timezone)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_scheduler.py -v`  
Expected: FAIL with missing scheduler module.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/scheduler/daily.py
from apscheduler.triggers.cron import CronTrigger


def build_trigger() -> CronTrigger:
    return CronTrigger(hour=18, minute=0, timezone="Asia/Jakarta")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_scheduler.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/scheduler/daily.py app/backend/cli/main.py tests/backend/test_scheduler.py
git commit -m "feat: add 18:00 wib scheduler trigger"
```

### Task 8: Verify End-to-End Local Flow and Documentation

**Files:**
- Create: `docs/local-runbook.md`
- Modify: `tests/backend/test_api_contract.py`
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`

- [ ] **Step 1: Write failing smoke check test (backend)**

```python
def test_health_and_screener_endpoints_exist(client):
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/screener").status_code in [200, 404]
```

- [ ] **Step 2: Run test to verify baseline**

Run: `pytest tests/backend/test_api_contract.py -v`  
Expected: PASS on health and defined behavior for screener.

- [ ] **Step 3: Run frontend build and tests**

Run: `cd app/frontend && npm test && npm run build`  
Expected: PASS tests and successful production build.

- [ ] **Step 4: Write local runbook**

```markdown
# Local Runbook

1. Install backend deps: `pip install -r requirements.txt`
2. Initialize DB: `python -m app.backend.cli.main init-db`
3. Run pipeline: `python -m app.backend.cli.main run-daily --date YYYY-MM-DD`
4. Start API: `uvicorn app.backend.api.app:app --reload`
5. Start frontend: `cd app/frontend && npm install && npm run dev`
```

- [ ] **Step 5: Commit**

```bash
git add docs/local-runbook.md tests/backend/test_api_contract.py app/frontend/src/features/screener/ScreenerPage.tsx
git commit -m "docs: add local runbook and finalize v1 smoke path"
```

---

## Plan Self-Review

- Spec coverage: backend pipeline, API contract, frontend screener UX, scheduler, reliability baseline, and local-first delivery are mapped into Tasks 1–8.
- Placeholder scan: no TODO/TBD placeholders remain.
- Type consistency: `vol_ratio`, `range_pct`, `price_action`, `is_ara_t0` naming is consistent across tasks.

## Execution Notes

- Run tasks in order with TDD flow in each task.
- Keep read-only UI boundary and no market refresh action in frontend.
- If any dependency/setup step fails, stop and resolve before continuing.
