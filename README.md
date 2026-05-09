# Fresh ARA Candidate

Web screener read-only saham Indonesia untuk kandidat **Fresh ARA** berbasis pola H-1 (quiet accumulation), sesuai PRD di `prd.md`.

## Status

- Core pipeline + scheduler + observability: ✅
- Screener API + analytics + export: ✅
- Watchlist + alert event flow + KPI baseline: ✅
- Frontend screener (responsive + PWA-ready): ✅
- Strategy revision (dynamic preset + fresh filter + tiered scoring + extended backtest metrics): ✅

## Scope v1

- Aplikasi bersifat **read-only display** (tanpa eksekusi order)
- Tidak ada tombol refresh market data di UI (refresh via CLI)

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite, APScheduler
- Frontend: React, TypeScript, Vite, Vitest
- Testing: pytest (backend), Vitest + Testing Library (frontend)

## Project Structure

```text
app/
  backend/
    api/
    cli/
    core/
    repositories/
    scheduler/
    services/
  frontend/
    src/
tests/
docs/
prd.md
```

## Prasyarat

- Python 3.10+
- Node.js 18+
- npm

## Setup Cepat (Local)

### 1) Backend

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python -c "from app.backend.core.db import init_db; init_db()"
uvicorn app.backend.api.app:app --reload
```

### 2) Frontend

```bash
npm --prefix app/frontend install
npm --prefix app/frontend run dev
```

### 3) Jalankan pipeline harian

```bash
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --universe-mode external_live
```

## Common CLI Commands

```bash
python -m app.backend.cli.main update-market --date YYYY-MM-DD --batch-size 50 --qps 2 --universe-mode external_live
python -m app.backend.cli.main backfill-market --start YYYY-MM-DD --end YYYY-MM-DD --qps 2 --batch-size 50
python -m app.backend.cli.main compute-features --date YYYY-MM-DD --feature-version v1
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset balanced
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --universe-mode external_live
python -m app.backend.cli.main schedule-screening --timezone Asia/Jakarta
```

## API Highlights

Base path: `/api/v1`

- Health/meta:
  - `GET /health`
  - `GET /meta/latest-screen-date`
  - `GET /meta/data-freshness`
  - `GET /meta/presets`
  - `GET /meta/job-runs`
- Screener:
  - `GET /screener`
  - `GET /screener/{ticker}`
  - `GET /screener/{ticker}/history`
- Analytics/export:
  - `GET /analytics/distribution`
  - `GET /analytics/backtest`
  - `GET /analytics/kpi`
  - `GET /export/screener.csv`
  - `GET /export/screener.xlsx`
- Watchlist/alerts:
  - `GET /watchlists`
  - `GET /watchlists/{watchlist_name}/tickers`
  - `POST /watchlists/{watchlist_name}/tickers`
  - `DELETE /watchlists/{watchlist_name}/tickers/{ticker}`
  - `GET /alerts/recent`

## Screening Strategy (Current)

- Preset threshold diterapkan dinamis di core screening (`conservative`, `balanced`, `aggressive`).
- `vol_ratio` menggunakan basis `avg_volume_5d` bila tersedia.
- Fresh filter aktif: `days_since_last_ara >= 5`.
- Price action menggunakan tiered scoring (`1.0 / 0.8 / 0.6 / 0.0`).
- Backtest endpoint menyediakan metrik tambahan: `hit_rate_1d`, `hit_rate_3d`, `avg_score_hit`, `avg_score_miss`, `distribution_by_pass_count`.

## CLI Playbook (By Scenario)

### 1) First-time setup data (disarankan)

```bash
python -m app.backend.cli.main backfill-market --start 2026-01-01 --end YYYY-MM-DD --qps 2 --batch-size 50
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 2 --batch-size 50 --universe-mode external_live
```

Kegunaan:
- Isi histori market dari awal periode kerja.
- Generate output screening terbaru yang langsung bisa dipakai di UI/API.

### 2) Operasional harian normal

```bash
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 2 --batch-size 50 --universe-mode external_live
```

Kegunaan:
- Menjalankan full pipeline harian end-to-end untuk tanggal target.

### 3) Saat ingin evaluasi preset tertentu

```bash
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset conservative
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset aggressive
```

Kegunaan:
- Membandingkan kandidat dan metrik antar preset.

### 4) Recovery ketika data market belum lengkap/kosong

```bash
python -m app.backend.cli.main update-market --date YYYY-MM-DD --qps 1 --batch-size 50 --universe-mode external_live
python -m app.backend.cli.main daily-smoke --date YYYY-MM-DD --qps 1 --batch-size 50 --universe-mode external_live
```

Jika masih gagal:
- turunkan `--qps` (mis. 1),
- ulangi `update-market`,
- lalu jalankan `run-daily` lagi.

### 5) Menjalankan scheduler otomatis

```bash
python -m app.backend.cli.main schedule-screening --timezone Asia/Jakarta
```

Kegunaan:
- Menyalakan penjadwalan screening otomatis sesuai timezone.

## Testing

Backend:

```bash
pytest -q
```

Frontend:

```bash
npm --prefix app/frontend run test
npm --prefix app/frontend run build
```

## Documentation

- PRD: [`prd.md`](./prd.md)
- Local runbook: [`docs/local-runbook.md`](./docs/local-runbook.md)
- Design spec: [`docs/superpowers/specs/2026-05-06-fresh-ara-screener-design.md`](./docs/superpowers/specs/2026-05-06-fresh-ara-screener-design.md)
- Implementation plan: [`docs/superpowers/plans/2026-05-06-fresh-ara-screener-implementation.md`](./docs/superpowers/plans/2026-05-06-fresh-ara-screener-implementation.md)
