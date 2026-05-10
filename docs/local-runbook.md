# Local Runbook

## A. Setup dasar

1. Install backend dependencies: `pip install -r requirements.txt`
2. Initialize database tables:
   - `python -c "from app.backend.core.db import init_db; init_db()"`
3. Start backend API:
   - `uvicorn app.backend.api.app:app --reload`
4. Install frontend dependencies:
   - `npm --prefix app/frontend install`
5. Start frontend dev server:
   - `npm --prefix app/frontend run dev`

## B. Skenario CLI operasional

### 1) First-time bootstrap data

```bash
python -m app.backend.cli.main backfill-market --start 2026-01-01 --end YYYY-MM-DD --qps 2 --batch-size 50
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 2 --batch-size 50 --universe-mode external_live
```

### 2) Rutinitas harian

```bash
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 2 --batch-size 50 --universe-mode external_live
```

### 3) Bandingkan preset

```bash
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset conservative --feature-version v2
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset aggressive --feature-version v2
```

### 4) Recovery jika data kosong/tidak complete

```bash
python -m app.backend.cli.main update-market --date YYYY-MM-DD --qps 1 --batch-size 50 --universe-mode external_live
python -m app.backend.cli.main daily-smoke --date YYYY-MM-DD --qps 1 --batch-size 50 --universe-mode external_live
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 1 --batch-size 50 --universe-mode external_live
```

## C. Parameter penting (ringkas)

- `--date`: tanggal target proses (`YYYY-MM-DD`).
- `--start` / `--end`: rentang tanggal untuk backfill/range mode compute-screening/export.
- `--preset`: preset screening (`conservative`, `balanced`, `aggressive`).
- `--feature-version`: versi fitur (`v1` legacy, `v2` rich fitur + indikator lanjutan).
- `--qps`: request per detik ke sumber market (atur ke bawah jika throttling/error meningkat).
- `--batch-size`: jumlah ticker per batch proses (lebih kecil = lebih stabil, lebih lambat).
- `--universe-mode`: mode universe ticker (`external_live` direkomendasikan untuk cakupan luas).
- `--timezone`: timezone scheduler otomatis.

## D. Status output yang perlu diperhatikan

- `update-market`
  - Jika incomplete: `[ALERT][MARKET] date=... fetched=... expected=... source=...`
- `daily-smoke`
  - Sukses: `[SMOKE][OK] ...`
  - Skip: `[SMOKE][SKIPPED] ...`
  - Alert: `[SMOKE][ALERT] ...`

## E. Verifikasi cepat

- Backend tests: `pytest -q`
- Frontend tests: `npm --prefix app/frontend run test`
- Frontend build: `npm --prefix app/frontend run build`
