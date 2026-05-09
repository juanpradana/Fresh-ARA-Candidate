# Fresh ARA Screening Strategy Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement revised Fresh ARA strategy with dynamic core presets, stricter freshness logic, tiered scoring, and expanded backtest metrics while preserving read-only product boundaries.

**Architecture:** Keep existing modular monolith (CLI + services + repository + API + frontend) and apply additive domain changes. Core strategy behavior is centralized in screening/scoring services, while repository/API expose richer result shape and analytics.

**Tech Stack:** Python, FastAPI, SQLAlchemy, SQLite, pytest, React, TypeScript, Vitest.

---

## File Structure Map

### Backend core/domain
- Modify: `app/backend/services/feature_engineering/service.py`
- Modify: `app/backend/services/screening/service.py`
- Modify: `app/backend/services/scoring/service.py`
- Modify: `app/backend/cli/commands/run_screening.py`
- Modify: `app/backend/repositories/sqlite/models.py`
- Modify: `app/backend/repositories/sqlite/repo.py`
- Modify: `app/backend/core/db.py` (column bootstrap only if needed)

### Backend API
- Modify: `app/backend/api/routers/screener.py`
- Modify: `tests/backend/test_api_contract.py`

### Frontend
- Modify: `app/frontend/src/shared/api/client.ts`
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Modify: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

### New backend tests
- Create: `tests/backend/test_run_screening_presets.py`
- Create: `tests/backend/test_feature_engineering_volume_ratio.py`
- Create: `tests/backend/test_fresh_filter.py`
- Create: `tests/backend/test_scoring_tiered.py`
- Create: `tests/backend/test_scoring_bb_bonus.py`
- Create: `tests/backend/test_backtest_metrics_extended.py`

---

### Task 1: Make preset thresholds fully dynamic in core screening

**Files:**
- Modify: `app/backend/services/screening/service.py`
- Modify: `app/backend/cli/commands/run_screening.py`
- Modify: `app/backend/repositories/sqlite/repo.py`
- Test: `tests/backend/test_run_screening_presets.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.services.screening.service import is_fresh_ara_candidate


def test_conservative_rejects_while_aggressive_accepts_same_row():
    row = {
        "vol_ratio": 0.65,
        "range_pct": 0.45,
        "price_action": 0.65,
        "is_ara_t0": 0,
    }

    conservative = {
        "vol_ratio_min": 0.85,
        "vol_ratio_max": 1.15,
        "range_pct_min": 0.50,
        "range_pct_max": 0.85,
        "price_action_max": 0.50,
    }
    aggressive = {
        "vol_ratio_min": 0.60,
        "vol_ratio_max": 1.40,
        "range_pct_min": 0.40,
        "range_pct_max": 1.20,
        "price_action_max": 0.90,
    }

    assert is_fresh_ara_candidate(row, conservative) is False
    assert is_fresh_ara_candidate(row, aggressive) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_run_screening_presets.py -v`  
Expected: FAIL because screening function currently hardcoded balanced and no preset argument.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/services/screening/service.py
from typing import Mapping


def is_fresh_ara_candidate(row: Mapping[str, float | int], preset: Mapping[str, float]) -> bool:
    return (
        float(preset["vol_ratio_min"]) <= float(row["vol_ratio"]) <= float(preset["vol_ratio_max"])
        and float(preset["range_pct_min"]) <= float(row["range_pct"]) <= float(preset["range_pct_max"])
        and float(row["price_action"]) < float(preset["price_action_max"])
        and int(row["is_ara_t0"]) == 0
    )
```

```python
# app/backend/repositories/sqlite/repo.py
# add helper (or equivalent) returning one preset row by name

def get_preset_by_name(preset_name: str) -> dict | None:
    ...
```

```python
# app/backend/cli/commands/run_screening.py
# resolve preset by name and pass to screening function
preset_row = get_preset_by_name(preset)
if preset_row is None:
    preset_row = get_preset_by_name("balanced")
...
passed = is_fresh_ara_candidate(features, preset_row)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_run_screening_presets.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/services/screening/service.py app/backend/cli/commands/run_screening.py app/backend/repositories/sqlite/repo.py tests/backend/test_run_screening_presets.py
git commit -m "feat: make screening thresholds dynamic per preset"
```

---

### Task 2: Align volume ratio to 5-day basis

**Files:**
- Modify: `app/backend/services/feature_engineering/service.py`
- Modify: `app/backend/repositories/sqlite/repo.py` (if historical data fetch helper needed)
- Test: `tests/backend/test_feature_engineering_volume_ratio.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.services.feature_engineering.service import compute_features


def test_compute_features_uses_vol_ratio_5d():
    row = {
        "volume": 1000.0,
        "prev_volume": 900.0,
        "avg_volume_5d": 800.0,
        "high": 105.0,
        "low": 100.0,
        "close": 102.0,
        "open": 101.0,
    }

    out = compute_features(row)
    assert round(out["vol_ratio"], 4) == 1.25
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_feature_engineering_volume_ratio.py -v`  
Expected: FAIL because current implementation uses `volume/prev_volume`.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/services/feature_engineering/service.py

def compute_features(row: dict) -> dict:
    avg_volume_5d = row.get("avg_volume_5d")
    vol_ratio = (row["volume"] / avg_volume_5d) if avg_volume_5d else 0.0
    range_pct = ((row["high"] - row["low"]) / row["close"] * 100.0) if row["close"] else 0.0
    price_action = abs(row["close"] - row["open"]) / row["open"] if row["open"] else 0.0
    return {
        "vol_ratio": vol_ratio,
        "range_pct": range_pct,
        "price_action": price_action,
        "is_ara_t0": 0,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_feature_engineering_volume_ratio.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/services/feature_engineering/service.py tests/backend/test_feature_engineering_volume_ratio.py
git commit -m "feat: align volume ratio with 5-day baseline"
```

---

### Task 3: Add strict freshness filter (`days_since_last_ara >= 5`)

**Files:**
- Modify: `app/backend/services/feature_engineering/service.py`
- Modify: `app/backend/services/screening/service.py`
- Modify: `app/backend/cli/commands/run_screening.py`
- Modify: `app/backend/repositories/sqlite/models.py`
- Modify: `app/backend/repositories/sqlite/repo.py`
- Test: `tests/backend/test_fresh_filter.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.services.screening.service import passes_fresh_filter


def test_fresh_filter_requires_min_five_days_since_last_ara():
    assert passes_fresh_filter(4) is False
    assert passes_fresh_filter(5) is True
    assert passes_fresh_filter(999) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_fresh_filter.py -v`  
Expected: FAIL because helper/rule does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/services/screening/service.py

def passes_fresh_filter(days_since_last_ara: int) -> bool:
    return int(days_since_last_ara) >= 5
```

```python
# integrate in is_fresh_ara_candidate(...)
and passes_fresh_filter(int(row["days_since_last_ara"]))
```

```python
# app/backend/cli/commands/run_screening.py
pass_fresh_check = 1 if int(features["days_since_last_ara"]) >= 5 else 0
# include in persisted payload/reason fields where relevant
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_fresh_filter.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/services/screening/service.py app/backend/services/feature_engineering/service.py app/backend/cli/commands/run_screening.py app/backend/repositories/sqlite/models.py app/backend/repositories/sqlite/repo.py tests/backend/test_fresh_filter.py
git commit -m "feat: enforce fresh ara filter by days-since-last-ara"
```

---

### Task 4: Implement tiered scoring

**Files:**
- Modify: `app/backend/services/scoring/service.py`
- Modify: `app/backend/cli/commands/run_screening.py`
- Test: `tests/backend/test_scoring_tiered.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.services.scoring.service import score_price_action_tier


def test_price_action_tiered_scoring_boundaries():
    assert score_price_action_tier(0.29) == 1.0
    assert score_price_action_tier(0.30) == 0.8
    assert score_price_action_tier(0.50) == 0.6
    assert score_price_action_tier(0.70) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_scoring_tiered.py -v`  
Expected: FAIL because tier helper does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/services/scoring/service.py

def score_price_action_tier(price_action: float) -> float:
    if price_action < 0.30:
        return 1.0
    if price_action < 0.50:
        return 0.8
    if price_action < 0.70:
        return 0.6
    return 0.0


def score_candidate(features: dict) -> float:
    score_vol = ...
    score_range = ...
    score_price = score_price_action_tier(float(features["price_action"]))
    return round((score_vol + score_range + score_price) / 3.0, 4)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_scoring_tiered.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/services/scoring/service.py app/backend/cli/commands/run_screening.py tests/backend/test_scoring_tiered.py
git commit -m "feat: add tiered scoring for price action"
```

---

### Task 5: Add optional BB squeeze bonus score

**Files:**
- Modify: `app/backend/services/feature_engineering/service.py`
- Modify: `app/backend/services/scoring/service.py`
- Modify: `app/backend/cli/commands/run_screening.py`
- Test: `tests/backend/test_scoring_bb_bonus.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.services.scoring.service import score_candidate


def test_bb_squeeze_bonus_increases_final_score():
    base = {
        "vol_ratio": 1.0,
        "range_pct": 0.75,
        "price_action": 0.4,
        "is_bb_squeeze_20": 0,
    }
    boosted = dict(base)
    boosted["is_bb_squeeze_20"] = 1

    assert score_candidate(boosted) > score_candidate(base)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_scoring_bb_bonus.py -v`  
Expected: FAIL because bonus scoring not implemented.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/services/scoring/service.py

def score_candidate(features: dict) -> float:
    ...
    bonus = 0.1 if int(features.get("is_bb_squeeze_20", 0)) == 1 else 0.0
    final = ((score_vol + score_range + score_price) / 3.0) + bonus
    return round(min(final, 1.0), 4)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_scoring_bb_bonus.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/services/feature_engineering/service.py app/backend/services/scoring/service.py app/backend/cli/commands/run_screening.py tests/backend/test_scoring_bb_bonus.py
git commit -m "feat: add optional bb squeeze bonus to scoring"
```

---

### Task 6: Expand result payload and API contract

**Files:**
- Modify: `app/backend/repositories/sqlite/models.py`
- Modify: `app/backend/repositories/sqlite/repo.py`
- Modify: `app/backend/api/routers/screener.py`
- Modify: `tests/backend/test_api_contract.py`
- Modify: `app/frontend/src/shared/api/client.ts`
- Modify: `app/frontend/src/features/screener/ScreenerPage.tsx`
- Modify: `app/frontend/src/features/screener/ScreenerPage.test.tsx`

- [ ] **Step 1: Write the failing test**

```python
def test_screener_detail_includes_fresh_and_scoring_components(client):
    res = client.get("/api/v1/screener/BBCA.JK?screen_date=2026-05-21&preset=balanced")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "days_since_last_ara" in data
    assert "score_price_action" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_api_contract.py -v`  
Expected: FAIL because fields are not exposed yet.

- [ ] **Step 3: Write minimal implementation**

```python
# repo serializer/enrichment: include new indicator + scoring fields in payload
# screener router: preserve envelope, return enriched fields from repo
```

```ts
// app/frontend/src/shared/api/client.ts
// extend ScreenerDetail/ScreenerRow types with new optional fields
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_api_contract.py -v`  
Expected: PASS.

Then run frontend targeted test:

Run: `npm --prefix app/frontend run test -- ScreenerPage.test.tsx`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/repositories/sqlite/models.py app/backend/repositories/sqlite/repo.py app/backend/api/routers/screener.py tests/backend/test_api_contract.py app/frontend/src/shared/api/client.ts app/frontend/src/features/screener/ScreenerPage.tsx app/frontend/src/features/screener/ScreenerPage.test.tsx
git commit -m "feat: expose revised screening fields in api and ui types"
```

---

### Task 7: Expand backtest metrics

**Files:**
- Modify: `app/backend/repositories/sqlite/repo.py`
- Modify: `app/backend/api/routers/screener.py`
- Test: `tests/backend/test_backtest_metrics_extended.py`

- [ ] **Step 1: Write the failing test**

```python
from app.backend.repositories.sqlite.repo import get_backtest_summary


def test_backtest_summary_includes_extended_metrics():
    summary = get_backtest_summary(start="2026-05-01", end="2026-05-31", preset="balanced", top_n=10)
    assert "hit_rate_1d" in summary
    assert "hit_rate_3d" in summary
    assert "avg_score_hit" in summary
    assert "avg_score_miss" in summary
    assert "distribution_by_pass_count" in summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/backend/test_backtest_metrics_extended.py -v`  
Expected: FAIL because metrics not present.

- [ ] **Step 3: Write minimal implementation**

```python
# app/backend/repositories/sqlite/repo.py
# extend get_backtest_summary return dict with:
# hit_rate_1d, hit_rate_3d, avg_score_hit, avg_score_miss, distribution_by_pass_count
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/backend/test_backtest_metrics_extended.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/backend/repositories/sqlite/repo.py app/backend/api/routers/screener.py tests/backend/test_backtest_metrics_extended.py
git commit -m "feat: extend backtest analytics metrics"
```

---

### Task 8: Full verification and documentation update

**Files:**
- Modify: `README.md`
- Modify: `docs/local-runbook.md`
- Modify: `prd.md` (only if threshold/config documentation must be synced)

- [ ] **Step 1: Run full backend tests**

Run: `pytest -q`  
Expected: PASS.

- [ ] **Step 2: Run frontend tests and build**

Run: `npm --prefix app/frontend run test && npm --prefix app/frontend run build`  
Expected: PASS.

- [ ] **Step 3: Update docs for revised strategy**

- Add section in `README.md` summarizing dynamic presets, freshness filter, and tiered scoring.
- Update `docs/local-runbook.md` with any changed pipeline assumptions.

- [ ] **Step 4: Run smoke pipeline command**

Run: `python -m app.backend.cli.main run-daily --date 2026-05-21 --preset balanced --batch-size 50 --qps 2`  
Expected: command completes and persists revised screening outputs.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/local-runbook.md prd.md
git commit -m "docs: sync strategy revision behavior and runbook"
```

---

## Plan Self-Review

- Spec coverage: all approved revision points are mapped (dynamic preset, 5d volume basis, freshness filter, tiered scoring, BB bonus, richer output, expanded metrics).
- Placeholder scan: no TODO/TBD placeholders remain.
- Type consistency: new fields are named consistently (`days_since_last_ara`, `is_bb_squeeze_20`, `pass_fresh_check`, `score_price_action`).

## Execution Notes

- Keep changes additive for API compatibility.
- Do not add trading-side actions; product remains read-only.
- If schema changes require migration support, update bootstrap path in `app/backend/core/db.py` within the same task that introduces the fields.
