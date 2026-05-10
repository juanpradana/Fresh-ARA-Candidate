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
python -m app.backend.cli.main compute-features --date YYYY-MM-DD --feature-version v2
python -m app.backend.cli.main compute-features --start YYYY-MM-DD --end YYYY-MM-DD --feature-version v2
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset balanced --feature-version v2
python -m app.backend.cli.main run-screening --start YYYY-MM-DD --end YYYY-MM-DD --preset balanced --feature-version v2
python -m app.backend.cli.main export-market-data --date YYYY-MM-DD --dataset features --feature-version v2 --output data/features.csv --format csv
python -m app.backend.cli.main export-market-data --start YYYY-MM-DD --end YYYY-MM-DD --dataset features --feature-version v2 --output data/features.parquet --format parquet
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --universe-mode external_live
python -m app.backend.cli.main daily-smoke --date YYYY-MM-DD --batch-size 50 --qps 2 --universe-mode external_live
python -m app.backend.cli.main schedule-screening --timezone Asia/Jakarta
```

## CLI Reference (Lengkap)

Base command:

```bash
python -m app.backend.cli.main <command> [options]
```

### 1) `update-market`

Fungsi:
- Ambil data market harian per ticker dari Yahoo Finance untuk tanggal tertentu.
- Menulis data ke `price_daily`.
- Menampilkan alert CLI jika hasil tidak complete.

Contoh:

```bash
python -m app.backend.cli.main update-market --date 2026-05-08 --batch-size 50 --qps 2 --universe-mode external_live
```

Opsi:
- `--date` (required): tanggal target (`YYYY-MM-DD`).
- `--batch-size` (default `50`): jumlah ticker per batch proses.
- `--qps` (default `2.0`): laju request per detik ke sumber market.
- `--universe-mode` (default `external_live`): mode universe ticker (`external_live` atau fallback internal).

Output penting:
- Jika incomplete: `[ALERT][MARKET] date=... fetched=... expected=... source=...`

### 2) `backfill-market`

Fungsi:
- Menjalankan `update-market` berulang untuk rentang tanggal.
- Dipakai untuk bootstrap/recovery histori data market.

Contoh:

```bash
python -m app.backend.cli.main backfill-market --start 2026-01-01 --end 2026-05-08 --qps 2 --batch-size 50
```

Opsi:
- `--start` (required): tanggal awal (`YYYY-MM-DD`).
- `--end` (required): tanggal akhir (`YYYY-MM-DD`).
- `--qps` (default `2.0`): laju request per detik.
- `--batch-size` (default `50`): jumlah ticker per batch.

Catatan:
- Tidak perlu full backfill ulang jika data rentang tersebut sudah lengkap.

### 3) `compute-features`

Fungsi:
- Hitung feature harian dari data market yang sudah ada.

Contoh:

```bash
python -m app.backend.cli.main compute-features --date 2026-05-08 --feature-version v1
```

Opsi:
- `--date` (required): tanggal target (`YYYY-MM-DD`).
- `--feature-version` (default `v1`): versi feature pipeline.

### 4) `run-screening`

Fungsi:
- Menjalankan scoring dan screening untuk tanggal + preset tertentu.

Contoh:

```bash
python -m app.backend.cli.main run-screening --date 2026-05-08 --preset balanced
```

Opsi:
- `--date` (required): tanggal target (`YYYY-MM-DD`).
- `--preset` (default `balanced`): `conservative`, `balanced`, atau `aggressive`.

### 5) `run-daily`

Fungsi:
- Orkestrasi full pipeline harian end-to-end:
  1. `update-market`
  2. `compute-features`
  3. `run-screening`
  4. capture alerts
- Menulis status job run + metadata observability (`expected`, `fetched`, `tickers_*`, `universe_*`).

Contoh:

```bash
python -m app.backend.cli.main run-daily --date 2026-05-08 --preset balanced --batch-size 50 --qps 2 --universe-mode external_live
```

Opsi:
- `--date` (required): tanggal target (`YYYY-MM-DD`).
- `--preset` (default `balanced`): preset screening.
- `--batch-size` (default `50`): ukuran batch untuk tahap update market.
- `--qps` (default `2.0`): laju request per detik untuk tahap update market.
- `--universe-mode` (default `external_live`): mode universe ticker.

Perilaku status:
- `success`: data market complete + screening selesai.
- `failed`: data market partial/incomplete atau exception pipeline.
- `skipped`: tidak ada market data pada tanggal run.

### 6) `daily-smoke`

Fungsi:
- Menjalankan smoke check cepat flow harian dan memberi sinyal operasional di terminal.

Contoh:

```bash
python -m app.backend.cli.main daily-smoke --date 2026-05-08 --batch-size 50 --qps 2 --universe-mode external_live
```

Opsi:
- `--date` (required): tanggal target (`YYYY-MM-DD`).
- `--batch-size` (default `50`): ukuran batch update market.
- `--qps` (default `2.0`): laju request per detik.
- `--universe-mode` (default `external_live`): mode universe ticker.

Output penting:
- `[SMOKE][OK] run_date=...`
- `[SMOKE][SKIPPED] run_date=... reason=...`
- `[SMOKE][ALERT] run_date=... error=...`

### 7) `schedule-screening`

Fungsi:
- Menyalakan scheduler otomatis berbasis APScheduler.
- Job harian memanggil flow `run-daily` (balanced, qps 2.0, batch 50).

Contoh:

```bash
python -m app.backend.cli.main schedule-screening --timezone Asia/Jakarta
```

Opsi:
- `--timezone` (default `Asia/Jakarta`): timezone scheduler.

Catatan operasional:
- Scheduler berjalan in-process; proses CLI harus tetap hidup.
- Trigger saat ini di-set jam 18:00 pada timezone yang dipilih.

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
- Mode `rich_v1` menambahkan sinyal lanjutan: `consecutive_green_days`, `rsi14`, `rsi14_slope`, `atr5_atr20_ratio`, `dist_to_52w_high_pct` (selain fitur teknikal kaya sebelumnya).
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
